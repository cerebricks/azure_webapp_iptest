from flask import Flask, request, jsonify
import requests 
import json
from azure.core.credentials import AzureKeyCredential
from azure.communication.callautomation import (CallAutomationClient, FileSource)
import os, time
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
    #TODO: Clean up this mess. Write Handling for validation and event 
    #validation_code = payload[0]['data']['validationCode']
    
    for event in payload:
        # Event-Informationen auslesen
        try:
            event_id = event["id"]
            event_type = event["eventType"]
            event_time = event["eventTime"]
            subject = event["subject"]
            topic = event["topic"]
        except Exception as e:
            print(e)
            event_id = event["id"]
            event_type = event["type"]
            event_time = event["time"]
            subject = event["subject"]

        # Daten für 'to' und 'from' extrahieren
        data = event.get("data", {})
        response = eventhandler(data, event_type)
    
    return response


def eventhandler(data, event_type):
    endpoint_url = os.getenv("endpointUrl")
    credential = AzureKeyCredential(os.getenv("CommunicationKey"))
    client = CallAutomationClient(endpoint_url, credential)
    callback_url = os.getenv("callBackUrl")
           
    match event_type:
        case 'Microsoft.Communication.IncomingCall':
            # Your unique Azure Communication service endpoint
            print("Incoming Connected")
            incoming_call_context = data['incomingCallContext']
            to_details = data.get("to", {}).get("phoneNumber", {}).get("value", "Unbekannt")
            from_details = data.get("from", {}).get("phoneNumber", {}).get("value", "Unbekannt")
            correlation_id = data.get("correlationId", "Unbekannt")
            call_connection_properties = client.answer_call(incoming_call_context, callback_url)
            # using call connection id, get call connection
            
            print(call_connection_properties)
            return jsonify({'response': '200'}), 200
        case 'Microsoft.Communication.CallConnected':
            print("Call Connected")
            call_connection_id = data['callConnectionId']
            call_connection = client.get_call_connection(call_connection_id)
            
            # from callconnection of result above, play media to all participants
            my_file = FileSource(url="https://sndup.net/rqvpp/d")
            print("got the file")
            print(my_file)
            
            try:
                my_file = FileSource(url="https://sndup.net/rqvpp/d")
                print("got the file")
                print(my_file)
                call_connection.play_media_to_all(my_file)
            except Exception as e:
                print(e)
            try:
                my_file = FileSource(url="https://dl.sndup.net/rqvpp/elevator%20(1).wav")
                print("got the file")
                print(my_file)
                call_connection.play_media_to_all(my_file)
            except Exception as e:
                print(e)
            time.sleep(3)
            call_connection.hang_up
            return jsonify({'response': '200'}), 200
            #https://github.com/microsoft/call-center-ai/blob/main/public/loading.wav
        case 'Microsoft.EventGrid.SubscriptionValidationEvent':
            validation_code = payload['validationCode']
            return jsonify({'validationResponse': validation_code}), 200
        case 'Microsoft.Communication.CallDisconnected':
            return jsonify({'response': '500', 'event_type': event_type }), 200
        case _:
            return jsonify({'response': '500','event_type': event_type}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
