from flask import Flask, request, jsonify
import requests 
import json
from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (CallAutomationClient)
import os
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
    validation_code = payload[0]['data']['validationCode']
    
    for event in payload:
        # Event-Informationen auslesen
        event_id = event["id"]
        event_type = event["eventType"]
        event_time = event["eventTime"]
        subject = event["subject"]
        topic = event["topic"]

        # Daten für 'to' und 'from' extrahieren
        data = event.get("data", {})
        to_details = data.get("to", {}).get("phoneNumber", {}).get("value", "Unbekannt")
        from_details = data.get("from", {}).get("phoneNumber", {}).get("value", "Unbekannt")
        correlation_id = data.get("correlationId", "Unbekannt")
        eventhandler(data, event_type)
    
    return jsonify({'validationResponse': validation_code})


def eventhandler(data, event_type):
    endpoint_url = os.getenv("endpointUrl")
    credential = AzureKeyCredential(os.getenv("CommunicationKey"))
    client = CallAutomationClient(endpoint_url, credential)
    callback_url = os.getenv("callBackUrl")
    incoming_call_context = data['incomingCallContext']
           
    match event_type:
        case 'Microsoft.Communication.IncomingCall':
            # Your unique Azure Communication service endpoint
            call_connection_properties = client.answer_call(incoming_call_context, callback_url)
            print(call_connection_properties)
        case _:
            return


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
