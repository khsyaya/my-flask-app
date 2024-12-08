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


# 判斷是否為 VPN 或代理 IP 特徵
def is_vpn(ip_address):
    # 使用一些常見的 VPN IP 特徵篩選（此處僅為示例，實際中需使用更多的數據）
    vpn_ranges = [
        "146.70.",  # 假設 VPN IP 范例
        "10.",      # 局域網 IP 的範圍
        "172.16.",
        "192.168.",
        "103."
    ]

    for vpn_range in vpn_ranges:
        if ip_address.startswith(vpn_range):
            print("Detected VPN/Proxy IP range.")
            return True
    return False


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試從 HTTP 請求標頭中獲取真實 IP
        real_ip_header = request.headers.get('X-Forwarded-For')
        if real_ip_header:
            real_ip = real_ip_header.split(',')[0]  # 提取第一個 IP 地址
            print("Extracted IP from X-Forwarded-For: ", real_ip)

            # 檢查是否是 VPN 或代理 IP
            if is_vpn(real_ip):
                print("IP is suspected to be a VPN or proxy IP. Trying third-party IP services...")
                # 如果檢測出 VPN，從第三方獲取真實 IP
                real_ip = get_real_ip()
            else:
                print("IP is valid and not suspected as VPN/proxy.")
        else:
            # 如果沒有 `X-Forwarded-For`，使用第三方 API
            print("No X-Forwarded-For found. Using third-party IP API...")
            real_ip = get_real_ip()
            if not real_ip:
                real_ip = request.remote_addr  # 最後回退到 remote_addr
            print("Extracted IP from get_real_ip or remote_addr: ", real_ip)

        # 從請求數據中提取 IP
        data = request.get_json()
        if 'ip' in data:
            received_ip = data['ip']
            print("Received IP Address: ", received_ip)

            print("Sending real IP instead: ", real_ip)
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
