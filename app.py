from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔥 Global variable (data store karne ke liye)
latest_data = {
    "moisture": "--",
    "temperature": "--",
    "humidity": "--"
}

@app.route('/')
def home():
    return f"""
    <h2>🌱 Smart Farming Dashboard</h2>
    <p><b>Moisture:</b> {latest_data['moisture']} %</p>
    <p><b>Temperature:</b> {latest_data['temperature']} °C</p>
    <p><b>Humidity:</b> {latest_data['humidity']} %</p>
    """

@app.route('/data', methods=['GET'])
def get_data():
    global latest_data

    moisture = request.args.get('moisture')
    temperature = request.args.get('temperature')
    humidity = request.args.get('humidity')

    # Save latest data
    latest_data["moisture"] = moisture
    latest_data["temperature"] = temperature
    latest_data["humidity"] = humidity

    print("----- NEW DATA -----")
    print(latest_data)

    # irrigation logic
    if float(moisture) < 30:
        irrigation = "ON"
    else:
        irrigation = "OFF"

    return jsonify({
        "status": "success",
        "irrigation": irrigation
    })
  
