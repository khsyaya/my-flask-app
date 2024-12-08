from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求


# 檢測 VPN/代理 IP 範疇
def is_vpn_or_proxy(ip_address):
    """
    檢測 IP 是否屬於 VPN/代理 IP 範疇。
    """
    vpn_ranges = [
        "146.70.", 
        "103.5.",
        "104.0.",
        "178.62.",
        "35.184.",
        "13.93.",
        "45.33.",
        "35.247.",
        "13.128.",
        "198.51."
    ]
    
    # 檢測 IP 是否匹配範疇
    for vpn_range in vpn_ranges:
        if ip_address.startswith(vpn_range):
            print(f"Detected VPN/Proxy IP range: {vpn_range}")
            return True
    return False


@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 嘗試提取真實 IP
        received_ip = request.headers.get('X-Forwarded-For')
        if received_ip:
            extracted_ip = received_ip.split(',')[0].strip()
            print("Extracted IP from X-Forwarded-For: ", extracted_ip)
        else:
            extracted_ip = request.remote_addr
            print("Extracted IP from request.remote_addr: ", extracted_ip)

        # 檢測是否屬於 VPN/代理 IP
        if is_vpn_or_proxy(extracted_ip):
            print("VPN/Proxy detected.")
            return jsonify({
                "status": "error",
                "message": "VPN/Proxy IP detected"
            }), 400

        # 返回解析的 IP
        print("IP verified as normal.")
        return jsonify({
            "status": "success",
            "real_ip": extracted_ip
        }), 200

    except Exception as e:
        print("Error during request handling: ", str(e))
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500


if __name__ == '__main__':
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)
    app.run(host="0.0.0.0", port=5000, debug=True)
