from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求

# IPStack API Key
IPSTACK_API_KEY = b65895c140a75e13d0fa796d5c0acaef  # 將此替換為你自己的 API Key


# 使用第三方服務 IPStack 進行真實 IP 查詢和 VPN 檢測
def fetch_real_ip(ip_address):
    try:
        url = f"http://api.ipstack.com/{ip_address}?access_key={IPSTACK_API_KEY}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("proxy", False) or data.get("vpn", False):  # 檢測是否使用 VPN 或 代理
                print("Detected VPN/Proxy IP via IPStack analysis.")
                return True
            print("IP is normal, no VPN/Proxy detected.")
            return False
        else:
            print("IPStack request failed with status code:", response.status_code)
            return False
    except Exception as e:
        print("Error during IPStack lookup: ", e)
        return False


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試從 HTTP 請求標頭中獲取真實 IP
        received_ip = request.headers.get('X-Forwarded-For')
        if received_ip:
            extracted_ip = received_ip.split(',')[0].strip()
            print("Extracted IP from X-Forwarded-For: ", extracted_ip)
        else:
            extracted_ip = request.remote_addr
            print("Extracted IP from request.remote_addr: ", extracted_ip)

        # 使用第三方服務進行 VPN 檢測
        if fetch_real_ip(extracted_ip):
            print("VPN/Proxy detected. Rejecting IP.")
            return jsonify({"status": "error", "message": "Detected VPN/Proxy IP"}), 400
        else:
            print("IP is clean. Sending IP directly.")
            return jsonify({"status": "success", "real_ip": extracted_ip}), 200

    except Exception as e:
        print("Error processing request: ", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    # 移除可能影響請求的代理設定
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)

    # 啟動 Flask 服務
    app.run(host="0.0.0.0", port=5000, debug=True)
