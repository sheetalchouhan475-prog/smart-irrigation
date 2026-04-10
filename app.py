from flask import Flask, request
from sklearn.tree import DecisionTreeClassifier
from twilio.rest import Client
import numpy as np

app = Flask(__name__)

# 🔹 Twilio credentials (yaha apna dalna)
account_sid = "L62UPLGEGF3V9CY7JFSS2NQ8"
auth_token = "2bf8608e12a9028c4940afb1adea5a9a"

client = Client(account_sid, auth_token)

# 🔹 WhatsApp numbers
twilio_number = 'whatsapp:+14155238886'
farmer_number = 'whatsapp:+917869707982'

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

# 📩 WhatsApp function
def send_whatsapp(message):
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=farmer_number
        )
        print("WhatsApp Sent ✅")
    except Exception as e:
        print("Error:", e)

# 📥 ESP32 data receive
@app.route('/data', methods=['GET'])
def receive_data():
    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        print("Data:", moisture, temp, humidity)

        # 🤖 ML Decision
        result = model.predict(np.array([[moisture, temp, humidity]]))[0]
        decision = "ON" if result == 1 else "OFF"

        # 📩 WhatsApp message
        msg = f"""🌱 Smart Farming Alert

Moisture: {moisture}
Temperature: {temp}°C
Humidity: {humidity}%

🚰 Pump: {decision}
"""
        send_whatsapp(msg)

        return decision

    except Exception as e:
        print("Error:", e)
        return "Error"

if __name__ == "__main__":
    app.run()
