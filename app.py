from flask import Flask, request
from datetime import datetime
from sklearn.tree import DecisionTreeClassifier
import numpy as np
from twilio.rest import Client

app = Flask(__name__)

# 🔹 Twilio credentials
account_sid = "ACf00f77d32e4e2194eb9d2b32ccdf5bd0"
auth_token = "16b54a6dd2d5fe40f9b138db1d375400"
twilio_number = "+16625640787"
your_number = "+919179309961"

client = Client(account_sid, auth_token)

# 🔹 Data storage
morning_data = []
evening_data = []

# 🔹 ML Model
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


# 🌐 DASHBOARD (NEW 🔥)
@app.route('/')
def dashboard():
    # Latest data choose
    if len(evening_data) > 0:
        data = evening_data[-1]
    elif len(morning_data) > 0:
        data = morning_data[-1]
    else:
        data = [0, 0, 0]

    moisture, temp, humidity = data

    return f"""
    <html>
    <head>
    <title>Smart Farming Dashboard</title>

    <style>
        body {{
            margin: 0;
            font-family: Arial;
            background: #e8f5e9;
            text-align: center;
        }}

        .header {{
            background: green;
            color: white;
            padding: 15px;
        }}

        .data-box {{
            margin-top: 60px;
            display: inline-block;
            padding: 25px;
            background: white;
            border-radius: 10px;
            box-shadow: 2px 2px 10px gray;
            font-size: 20px;
        }}

        .footer {{
            position: fixed;
            bottom: 10px;
            width: 100%;
            display: flex;
            justify-content: space-between;
            padding: 0 20px;
            font-size: 14px;
        }}

        .left {{
            text-align: left;
        }}

        .right {{
            text-align: right;
        }}
    </style>
    </head>

    <body>

    <!-- 🔝 Header -->
    <div class="header">
        <h1>Shivajirao Kadam Group of Institutes</h1>
        <h3>From ECE Department</h3>
    </div>

    <h2>Smart Farming Dashboard 🌱</h2>

    <!-- 📊 Center Data -->
    <div class="data-box">
        <p>🌱 Moisture: {moisture}</p>
        <p>🌡️ Temperature: {temp}</p>
        <p>💧 Humidity: {humidity}</p>
    </div>

    <!-- 👇 Footer -->
    <div class="footer">
        <div class="left">
            <b>Created by:</b><br>
            Pramila Yadav<br>
            Sheetal Chouhan<br>
            Mohit Verma
        </div>

        <div class="right">
            <b>Guided by:</b><br>
            Dr. Moumita Das
        </div>
    </div>

    </body>
    </html>
    """


# 📥 Data receive
@app.route('/data', methods=['GET'])
def receive_data():
    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        now = datetime.now()
        hour = now.hour

        if 4 <= hour < 7:
            morning_data.append([moisture, temp, humidity])
        elif 7 <= hour < 16:
            evening_data.append([moisture, temp, humidity])

        return "OK"

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
    except Exception as e:
        print("SMS Error:", e)


# 🤖 Decision
@app.route('/decision', methods=['GET'])
def decision():
    global last_morning_sent, last_evening_sent

    now = datetime.now()
    hour = now.hour

    if 7 <= hour <= 8 and not last_morning_sent:

        if len(morning_data) == 0:
            return "NO_DATA"

        avg_m = sum(d[0] for d in morning_data) / len(morning_data)
        avg_t = sum(d[1] for d in morning_data) / len(morning_data)
