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

        now = datetime.now()
        hour = now.hour

        # 🌅 Morning data (4–7)
        if 4 <= hour < 7:
            morning_data.append([moisture, temp, humidity])

        # 🌇 Evening data (7–16)
        elif 7 <= hour < 16:
            evening_data.append([moisture, temp, humidity])

        print("Stored:", moisture, temp, humidity)
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

# 🤖 Decision route@app.route('/decision', methods=['GET'])
def decision():
    global last_morning_sent, last_evening_sent

    now = datetime.now()
    hour = now.hour

    # 🌅 Morning decision (7–8 AM)
    if 7 <= hour <= 8 and not last_morning_sent:

        if len(morning_data) == 0:
            return "NO_DATA"

        avg_m = sum(d[0] for d in morning_data) / len(morning_data)
        avg_t = sum(d[1] for d in morning_data) / len(morning_data)
        avg_h = sum(d[2] for d in morning_data) / len(morning_data)

        result = model.predict(np.array([[avg_m, avg_t, avg_h]]))[0]
        decision_text = "ON" if result == 1 else "OFF"

        send_sms(f"Morning (4-7 data): Pump {decision_text}")

        last_morning_sent = True
        return decision_text

    # 🌇 Evening decision (4–5 PM)
    elif 16 <= hour <= 17 and not last_evening_sent:

        if len(evening_data) == 0:
            return "NO_DATA"

        avg_m = sum(d[0] for d in evening_data) / len(evening_data)
        avg_t = sum(d[1] for d in evening_data) / len(evening_data)
        avg_h = sum(d[2] for d in evening_data) / len(evening_data)

        result = model.predict(np.array([[avg_m, avg_t, avg_h]]))[0]
        decision_text = "ON" if result == 1 else "OFF"

        send_sms(f"Evening (7-4 data): Pump {decision_text}")

        last_evening_sent = True
        return decision_text

    return "NO_ACTION"

    # 🌇 Evening
    elif 16 <= hour <= 19 and not last_evening_sent:
        last_evening_sent = True

        msg = f"Evening Update:\nMoisture={avg_m:.1f}%\nTemp={avg_t:.1f}C\nHumidity={avg_h:.1f}%\nPump={decision_text}"
        send_sms(msg)

        return decision_text

    return "NO_ACTION"

# 🔄 Reset (next day)
@app.route('/reset', methods=['GET'])
def reset():
    global last_morning_sent, last_evening_sent, daily_data

    last_morning_sent = False
    last_evening_sent = False
    morning_data = []
    evening_data = []
    return "Reset Done"

if __name__ == "__main__":
    app.run()
