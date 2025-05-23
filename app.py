from flask import Flask, request, jsonify
import requests 
import json
app = Flask(__name__)
@app.route("/")
def home():
    return "Hello from Azure Web App!"

@app.route("/myip")
def get_my_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        return f"Outbound IP address is: {ip}"
    except Exception as e:
        return f"Error getting IP: {e}", 500


@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    print(payload)
    try:
        payload = json.loads(payload)
    except Exception as e:
        return f"Error parsing json: {e}", 500
    print(payload)
    validation_code = payload['data']['validationCode']
    
    return jsonify({'validationResponse': validation_code})
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
