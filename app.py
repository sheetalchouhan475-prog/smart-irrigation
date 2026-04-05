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

# 🔹 Data store
daily_data = []

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

# 🔹 Flags (SMS control)
last_morning_sent = False
last_evening_sent = False

# 📥 Data receive
@app.route('/data', methods=['GET'])
def receive_data():
    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        daily_data.append([moisture, temp, humidity])

        print("Data:", moisture, temp, humidity)
        return "OK"
    except:
        return "Error"

# 📩 SMS function
def send_sms(message):
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=your_number
        )
        print("SMS Sent:", message)
    except Exception as e:
        print("SMS Error:", e)

# 🤖 Decision route
@app.route('/decision', methods=['GET'])
def decision():
    global last_morning_sent, last_evening_sent

    now = datetime.now()
    hour = now.hour

    if len(daily_data) == 0:
        return "NO_DATA"

    # 🔹 Average
    avg_m = sum(d[0] for d in daily_data) / len(daily_data)
    avg_t = sum(d[1] for d in daily_data) / len(daily_data)
    avg_h = sum(d[2] for d in daily_data) / len(daily_data)

    result = model.predict(np.array([[avg_m, avg_t, avg_h]]))[0]

    decision_text = "ON" if result == 1 else "OFF"

    # 🌅 Morning
    if 6 <= hour <= 9 and not last_morning_sent:
        last_morning_sent = True

        msg = f"Morning Update:\nMoisture={avg_m:.1f}%\nTemp={avg_t:.1f}C\nHumidity={avg_h:.1f}%\nPump={decision_text}"
        send_sms(msg)

        return decision_text

    # 🌇 Evening
    elif 16 <=
