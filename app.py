from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求

# IPStack API Key
IPSTACK_API_KEY = "b65895c140a75e13d0fa796d5c0acaef"  # 將此處替換為你實際的 IPStack Key


# 使用 IPStack 進行真實 IP 檢測
def fetch_real_ip(ip_address):
    try:
        # 建立 IPStack 請求 URL
        url = f"http://api.ipstack.com/{ip_address}?access_key={IPSTACK_API_KEY}"
        print(f"Requesting IPStack URL: {url}")  # 調試日誌
        
        # 發送請求
        response = requests.get(url, timeout=10)  # 增加超時時間
        print("HTTP Response status code:", response.status_code)  # 確認 HTTP 狀態碼

        # 檢查請求是否成功
        if response.status_code == 200:
            print("IPStack Response JSON: ", response.json())  # 顯示完整返回 JSON
            
            # 檢查 VPN/Proxy 屬性
            if response.json().get("proxy", False) or response.json().get("vpn", False):
                print("Detected VPN/Proxy IP detected via IPStack response.")
                return True  # 表示是 VPN 或代理 IP
            else:
                print("IPStack analysis clean, no VPN/Proxy detected.")
                return False  # 表示不是 VPN 或代理 IP
        else:
            print("Request failed. Response returned:", response.text)
            return False
    except Exception as e:
        print("Exception during IPStack request:", e)
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

        # 測試是否為 VPN/Proxy
        print("Checking VPN/Proxy status via IPStack...")
        is_vpn_or_proxy = fetch_real_ip(extracted_ip)

        if is_vpn_or_proxy:
            print("VPN/Proxy detected based on IPStack analysis. Sending error response.")
            return jsonify({"status": "error", "message": "Detected VPN/Proxy IP"}), 400
        else:
            print("No VPN/Proxy detected. Sending extracted IP back to client.")
            return jsonify({"status": "success", "real_ip": extracted_ip}), 200

    except Exception as e:
        print("Error processing request: ", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    # 移除可能影響請求的代理設定
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)

    # 啟動 Flask 服務
    print("Starting server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
