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
                    print("Successfully fetched real IP: ", response.text)
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
        data = request.get_json()

        if 'ip' in data:
            received_ip = data['ip']
            print("Received IP Address: ", received_ip)

            real_ip = get_real_ip()

            if real_ip:
                print("Sending real IP instead: ", real_ip)
                return jsonify({"status": "success", "received_ip": real_ip}), 200
            else:
                return jsonify({"status": "error", "message": "Could not fetch real IP"}), 500

        else:
            return jsonify({"status": "error", "message": "No IP found"}), 400

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500
