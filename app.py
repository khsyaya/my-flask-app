from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求

@app.route('/log', methods=['POST'])
def log_ip():
    try:
        # 從 POST 請求中獲取數據
        data = request.get_json()
        
        # 檢查請求數據是否包含 IP 地址
        if 'ip' in data:
            print("Received IP Address: ", data['ip'])
            return jsonify({"status": "success", "received_ip": data['ip']}), 200
        else:
            return jsonify({"status": "error", "message": "No IP found"}), 400
    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


if __name__ == '__main__':
    # 啟動 Flask 應用
    app.run(host="0.0.0.0", port=8000)
