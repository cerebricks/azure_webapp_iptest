from flask import Flask
import requests, jsonify

app = Flask(__name__)

def parse_request(req):
"""
Parses application/json request body data into a Python dictionary
"""
    payload = req.get_data()
    payload = unquote_plus(payload)
    payload = re.sub('payload=', '', payload)
    payload = json.loads(payload)
    return payload

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
    payload = parse_request(request)
    print payload['p']

    return (payload, 200, None)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
