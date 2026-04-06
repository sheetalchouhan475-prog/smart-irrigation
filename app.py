from flask import Flask, request
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from twilio.rest import Client
import pandas as pd   # 🔥 NEW

app = Flask(__name__)

# 🔹 Twilio credentials
account_sid = "ACf00f77d32e4e2194eb9d2b32ccdf5bd0"
auth_token = "40f31076b03c00fc3f1856e9f9d26d6c"
twilio_number = "+16625640787"
your_number = "+919179309961"

client = Client(account_sid, auth_token)

# 🔹 Latest sensor data
latest_data = [0, 0, 0]

# 🔹 SMS control
last_alert_sent = False


# 🔥 =========================
# 🔥 ML MODEL (CSV BASED)
# 🔥 =========================

# CSV load karo
data = pd.read_csv("data.csv")

# ⚠️ Yaha apne CSV ke column name dalna
# Example assume kar ra:
# moisture, temperature, humidity, label

X = data[['moisture', 'temperature', 'humidity']]
y = data['label']

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained using CSV ✅")


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


# 📥 DATA + ML + SMS
@app.route('/data', methods=['GET'])
def receive_data():
    global latest_data, last_alert_sent

    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        latest_data = [moisture, temp, humidity]

        # 🔥 ML prediction (REAL DATA)
        result = model.predict([[moisture, temp, humidity]])[0]

        # 🔥 SMS only when needed
        if result == 1 and not last_alert_sent:
            send_sms(f"""
🚨 Irrigation Required!

🌱 Moisture: {moisture:.1f}%
🌡 Temp: {temp:.1f}°C
💧 Humidity: {humidity:.1f}%
""")
            last_alert_sent = True

        if result == 0:
            last_alert_sent = False

        print("Data:", latest_data, "Decision:", result)

        return "ON" if result == 1 else "OFF"

    except Exception as e:
        print("Error:", e)
        return "Error"


# 📩 SMS
def send_sms(message):
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=your_number
        )
        print("SMS Sent")
    except Exception as e:
        import traceback
        print("FULL ERROR")
        traceback.print_exc()


if __name__ == "__main__":
    app.run()
