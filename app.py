from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 啟用 CORS 支持，允許跨域請求

@app.route('/log', methods=['POST'])
def log_ip():
    """
    從請求數據中接收 IP，並進行處理後返回。
    """
    try:
        # 從請求獲取數據
        data = request.get_json()
        
        # 檢查請求數據中是否包含 IP
        if 'ip' in data:
            received_ip = data['ip']  # 提取 IP 地址
            print("Received IP Address: ", received_ip)  # 後端打印接收到的 IP
            
            # 返回收到的 IP
            return jsonify({"status": "success", "received_ip": received_ip}), 200
        else:
            return jsonify({"status": "error", "message": "No IP found"}), 400

    except Exception as e:
        print("Error processing request:", str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500


# 啟動服務
if __name__ == '__main__':
    app.run(debug=True)
