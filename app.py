from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求


# 檢測 VPN/代理 IP 範疇
def is_vpn_or_proxy(ip_address):
    # 定義常見 VPN/代理 IP 範疇，這裡可以擴展更多範疇。
    vpn_ranges = [
        "146.70.",  # 常見的 VPN IP 範疇之一
        "103.5.", 
        "104.0.", 
        "178.62.",
        "35.184.",
        "13.93.",
        "45.33."
    ]
    for vpn_range in vpn_ranges:
        if ip_address.startswith(vpn_range):
            print("Detected VPN/Proxy IP range: ", vpn_range)
            return True
    return False


# 使用第三方服務進行真實 IP 查詢
def fetch_real_ip():
    try:
        # 使用外部 IP 检测服务，如 ipify 或其他第三方服務
        urls = [
            "https://api64.ipify.org",
            "https://api.my-ip.io/ip",
            "https://ifconfig.me/ip"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print("Fetched real IP via third-party service: ", response.text)
                    return response.text
            except Exception as e:
                print("Failed to fetch IP from URL: ", url, " Error: ", e)
        
        return None
    except Exception as e:
        print("Error while calling IP service: ", e)
        return None


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試從 HTTP 請求標頭中獲取真實 IP
        received_ip = request.headers.get('X-Forwarded-For')
        if received_ip:
            extracted_ip = received_ip.split(',')[0]  # 獲取第一個 IP
            print("Extracted IP from X-Forwarded-For: ", extracted_ip)
        else:
            extracted_ip = request.remote_addr  # 如果無法從標頭中獲取，退而使用 `remote_addr`
            print("Extracted IP from request.remote_addr: ", extracted_ip)

        # 檢測是否是 VPN/代理 IP 範疇
        if is_vpn_or_proxy(extracted_ip):
            print("VPN/Proxy detected. Fetching real IP...")
            real_ip = fetch_real_ip()  # 從第三方服務動態查詢真實 IP
            if real_ip:
                print("Sending real IP fetched dynamically: ", real_ip)
                return jsonify({"status": "success", "real_ip": real_ip}), 200
            else:
                print("Failed to fetch real IP. Falling back to received IP.")
                return jsonify({"status": "error", "message": "Could not resolve real IP"}), 500
        else:
            print("No VPN/Proxy detected. Sending received IP directly.")
            return jsonify({"status": "success", "real_ip": extracted_ip}), 200

    except Exception as e:
        print("Error processing request: ", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    app.run(host="0.0.0.0", port=5000)
