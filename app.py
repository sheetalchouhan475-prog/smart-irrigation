from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route (check server running)
@app.route('/')
def home():
    return "Smart Farming Server Running 🚀"


# ESP32 se data receive karne ke liye API
@app.route('/data', methods=['GET'])
def get_data():
    try:
        # ESP32 se values lena
        moisture = float(request.args.get('moisture'))
        temperature = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        print("Moisture:", moisture)
        print("Temperature:", temperature)
        print("Humidity:", humidity)

        # Simple logic (irrigation decision)
        if moisture > 2000 or Temperature > 30 or Humidity < 40:
    irrigation = "ON"
     else:
    irrigation = "OFF"

        # Response ESP32 ko bhejna
        return jsonify({
            "status": "success",
            "irrigation": irrigation
        })

    except:
        return jsonify({
            "status": "error",
            "message": "Invalid data"
        })


if __name__ == '__main__':
    app.run(debug=True)
