from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Twilio credentials
account_sid = 'ACf00f77d32e4e2194eb9d2b32ccdf5bd0'
auth_token = '16b54a6dd2d5fe40f9b138db1d375400'
client = Client(account_sid, auth_token)

# Twilio & user number
twilio_number = '+16625640787'
your_number = '+919179309961'

# Data store
latest_data = {
    "moisture": "--",
    "temperature": "--",
    "humidity": "--",
    "irrigation": "--"
}

sms_sent = False

@app.route('/')
def home():
    return f"""
    <h2>🌱 Smart Farming Dashboard</h2>
    <p><b>Moisture:</b> {latest_data['moisture']} %</p>
    <p><b>Temperature:</b> {latest_data['temperature']} °C</p>
    <p><b>Humidity:</b> {latest_data['humidity']} %</p>
    <p><b>Irrigation Status:</b> {latest_data['irrigation']}</p>
    """

@app.route('/data', methods=['GET'])
def get_data():
    global latest_data, sms_sent

    moisture = float(request.args.get('moisture'))
    temperature = float(request.args.get('temperature'))
    humidity = float(request.args.get('humidity'))

    # 🔥 SMART IRRIGATION LOGIC
    if (moisture < 40 and temperature > 25 and humidity < 50):
        irrigation = "Irrigation Required ✅"
        pump = "ON"

        # 📱 SMS SEND
        if not sms_sent:
            message = client.messages.create(
                body=f"⚠️ Irrigation Required!\nMoisture: {moisture}%\nTemp: {temperature}C",
                from_=twilio_number,
                to=your_number
            )
            sms_sent = True

    else:
        irrigation = "Irrigation Not Required ❌"
        pump = "OFF"
        sms_sent = False

    # Store data
    latest_data["moisture"] = moisture
    latest_data["temperature"] = temperature
    latest_data["humidity"] = humidity
    latest_data["irrigation"] = irrigation

    return jsonify({
        "status": "success",
        "irrigation": pump
    })
