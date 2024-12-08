from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求


# 檢測 VPN/代理 IP 範疇
def is_vpn_or_proxy(ip_address):
    """
    檢測是否屬於常見的 VPN/代理 IP 範疇。
    """
    vpn_ranges = [
        "146.70.",  # 常見的 VPN/代理 IP 範疇
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

        # 檢測是否是 VPN/代理 IP 範疇
        if is_vpn_or_proxy(extracted_ip):
            print("Detected VPN/Proxy, rejecting request.")
            return jsonify({"status": "error", "message": "Detected VPN/Proxy IP, cannot determine real IP"}), 400
        else:
            print("No VPN/Proxy detected, sending IP as-is.")
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
