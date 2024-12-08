from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求


# 測試多個 IP API
def get_real_ip():
    try:
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)

        urls = [
            "https://api64.ipify.org",
            "https://api.my-ip.io/ip",
            "https://ifconfig.me/ip"
        ]

        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print("Successfully fetched real IP from API: ", response.text)
                    return response.text
            except Exception as e:
                print(f"Failed to fetch IP from {url}: {e}")
        
        return None
    except Exception as e:
        print("Error while calling IP API: ", e)
        return None


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試從 HTTP 請求標頭中獲取真實 IP
        real_ip_header = request.headers.get('X-Forwarded-For')
        if real_ip_header:
            real_ip = real_ip_header.split(',')[0]  # 獲取第一個 IP 地址
            print("Extracted IP from X-Forwarded-For: ", real_ip)
        else:
            # 如果沒有 X-Forwarded-For，使用 get_real_ip()
            real_ip = get_real_ip()
            if not real_ip:
                real_ip = request.remote_addr  # 作為最後的回退選項
            print("Extracted IP from get_real_ip or remote_addr: ", real_ip)

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
