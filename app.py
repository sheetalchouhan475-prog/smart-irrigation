from flask import Flask, request
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from twilio.rest import Client

app = Flask(__name__)

# 🔹 Twilio credentials
account_sid = "ACf00f77d32e4e2194eb9d2b32ccdf5bd0"
auth_token = "16b54a6dd2d5fe40f9b138db1d375400"
twilio_number = "+6625640787"
your_number = "+919179309961"

client = Client(account_sid, auth_token)

# 🔹 Data storage
morning_data = []
evening_data = []
latest_data = [0, 0, 0]

# 🔹 ML Model (training)
X = [
    [30, 35, 40],
    [70, 25, 60],
    [20, 38, 30],
    [80, 22, 70],
    [25, 36, 35]
]
y = [1, 0, 1, 0, 1]

model = DecisionTreeClassifier()
model.fit(X, y)

# 🔹 Flags
last_morning_sent = False
last_evening_sent = False


# 🌐 DASHBOARD
@app.route('/')
def dashboard():
    moisture, temp, humidity = latest_data

    return f"""
    <html>
    <head>
    <title>Smart Farming Dashboard</title>
    <style>
        body {{
            font-family: Arial;
            text-align: center;
            background: #e8f5e9;
        }}
        .box {{
            margin-top: 50px;
            padding: 20px;
            background: white;
            display: inline-block;
            border-radius: 10px;
            box-shadow: 2px 2px 10px gray;
        }}
    </style>
    </head>
    <body>

    <h1>Smart Farming Dashboard 🌱</h1>

    <div class="box">
        <p>🌱 Moisture: {moisture}</p>
        <p>🌡️ Temperature: {temp}</p>
        <p>💧 Humidity: {humidity}</p>
    </div>

    </body>
    </html>
    """


# 📥 Data receive
@app.route('/data', methods=['GET'])
def receive_data():
    global latest_data

    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        hour = datetime.now().hour

        # 🔥 Always update (dashboard ke liye)
        latest_data = [moisture, temp, humidity]

        # 🌅 Morning data (4–7)
        if 4 <= hour < 7:
            morning_data.append([moisture, temp, humidity])

        # 🌇 Evening data (7–16)
        elif 7 <= hour < 16:
            evening_data.append([moisture, temp, humidity])

        print("Received:", latest_data)

        return "OK"

    except Exception as e:
        print("Error:", e)
        return "Error"


# 📩 SMS function
def send_sms(message):
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=your_number
        )
        print("SMS Sent")
    except Exception as e:
        print("SMS Error:", e)


# 🤖 Decision
@app.route('/decision', methods=['GET'])
def decision():
    global last_morning_sent, last_evening_sent

    hour = datetime.now().hour

    # 🌅 Morning decision (7–8)
    if 7 <= hour <= 8 and not last_morning_sent:

        if len(morning_data) == 0:
            return "NO_DATA"

        avg = np.mean(morning_data, axis=0)
        result = model.predict([avg])[0]

        # 🔥 SMS ONLY if irrigation required
        if result == 1:
            send_sms(f"""
🚨 Irrigation Required (Morning)

🌱 Moisture: {avg[0]:.1f}%
🌡 Temp: {avg[1]:.1f}°C
💧 Humidity: {avg[2]:.1f}%
""")

        last_morning_sent = True
        return "ON" if result == 1 else "OFF"

    # 🌇 Evening decision (16–17)
    elif 16 <= hour <= 17 and not last_evening_sent:

        if len(evening_data) == 0:
            return "NO_DATA"

        avg = np.mean(evening_data, axis=0)
        result = model.predict([avg])[0]

        # 🔥 SMS ONLY if irrigation required
        if result == 1:
            send_sms(f"""
🚨 Irrigation Required (Evening)

🌱 Moisture: {avg[0]:.1f}%
🌡 Temp: {avg[1]:.1f}°C
💧 Humidity: {avg[2]:.1f}%
""")

        last_evening_sent = True
        return "ON" if result == 1 else "OFF"

    return "NO_ACTION"


# 🔄 Reset
@app.route('/reset', methods=['GET'])
def reset():
    global morning_data, evening_data
    global last_morning_sent, last_evening_sent

    morning_data = []
    evening_data = []
    last_morning_sent = False
    last_evening_sent = False

    return "Reset Done"


if __name__ == "__main__":
    app.run()
