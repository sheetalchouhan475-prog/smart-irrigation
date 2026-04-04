from flask import Flask, request, jsonify

app = Flask(__name__)

latest_data = {
    "moisture": "--",
    "temperature": "--",
    "humidity": "--",
    "irrigation": "--"
}

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
    global latest_data

    moisture = float(request.args.get('moisture'))
    temperature = float(request.args.get('temperature'))
    humidity = float(request.args.get('humidity'))

    # 🔥 SMART LOGIC
    if (moisture < 30 and temperature > 25 and humidity < 50):
        irrigation = "Irrigation Required ✅"
        pump = "ON"
    else:
        irrigation = "Irrigation Not Required ❌"
        pump = "OFF"

    # Store data
    latest_data["moisture"] = moisture
    latest_data["temperature"] = temperature
    latest_data["humidity"] = humidity
    latest_data["irrigation"] = irrigation

    print("----- NEW DATA -----")
    print(latest_data)

    return jsonify({
        "status": "success",
        "irrigation": pump   # ESP32 ke liye ON/OFF hi bhejna hai
    })
