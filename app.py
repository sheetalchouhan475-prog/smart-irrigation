from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Smart Farming Server Running 🚀"

@app.route('/data', methods=['GET'])
def get_data():
    moisture = request.args.get('moisture')
    temperature = request.args.get('temperature')
    humidity = request.args.get('humidity')

    # 🔥 YEH ADD KARO (IMPORTANT)
    print("----- NEW DATA RECEIVED -----")
    print("Moisture:", moisture)
    print("Temperature:", temperature)
    print("Humidity:", humidity)

    # irrigation logic
    if float(moisture) < 30:
        irrigation = "ON"
    else:
        irrigation = "OFF"

    return jsonify({
        "status": "success",
        "irrigation": irrigation
    })
