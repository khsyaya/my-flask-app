from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求


# 測試多個 IP API 來獲取真實 IP
def get_real_ip():
    try:
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        urls = [
            "https://api64.ipify.org",
            "https://api.my-ip.io/ip",
            "https://ifconfig.me/ip",
            "https://checkip.amazonaws.com"
        ]

        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"IP fetched from {url}: {response.text}")
                    return response.text
            except Exception as e:
                print(f"Failed to fetch IP from {url}: {e}")
        
        return None
    except Exception as e:
        print("Error while calling IP API: ", e)
        return None


# 判斷 IP 是否屬於常見 VPN/代理 IP 範疇
def is_vpn(ip_address):
    # 自定義常見 VPN / 代理 IP 檢測範疇
    vpn_ranges = [
        "146.70.",
        "103.",
        "185.",
        "10.",
        "172.16.",
        "192.168.",
        "34.83.",  # Google Cloud IP 範疇，通常用於 VPN
    ]

    # 檢查 IP 是否匹配範疇
    for vpn_range in vpn_ranges:
        if ip_address.startswith(vpn_range):
            print(f"Detected VPN/Proxy IP range: {vpn_range}")
            return True
    return False


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試從 HTTP 請求標頭中獲取真實 IP
        real_ip_header = request.headers.get('X-Forwarded-For')
        if real_ip_header:
            real_ip = real_ip_header.split(',')[0]
            print("Extracted IP from X-Forwarded-For: ", real_ip)

            # 檢測是否為 VPN
            if is_vpn(real_ip):
                print("Detected VPN/Proxy. Replacing with real IP (Taiwan location).")
                # 替換成手動設定的真實 IP，例如台灣地區 IP 地址
                real_ip = "101.12.0.1"  # 將此處的 IP 替換為你的真實 IP 地址
            else:
                print("IP is valid and not suspected as VPN/proxy.")
        else:
            # 若無法獲取 X-Forwarded-For，回退到第三方 IP
            print("No X-Forwarded-For found. Attempting to fetch real IP from third-party IP service...")
            real_ip = "101.12.0.1"  # 將此處的 IP 替換為你的真實 IP 地址

        # 檢查用戶數據請求內容
        data = request.get_json()
        if 'ip' in data:
            received_ip = data['ip']
            print("Received IP Address: ", received_ip)

            print("Sending processed IP: ", real_ip)
            return jsonify({"status": "success", "real_ip": real_ip}), 200
        else:
            return jsonify({"status": "error", "message": "No IP found"}), 400

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    app.run(host="0.0.0.0", port=5000)
