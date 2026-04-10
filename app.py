# -*- coding: utf-8 -*-

from flask import Flask, request
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import requests
from twilio.rest import Client

app = Flask(__name__)

# 🔹 Twilio WhatsApp credentials
account_sid = "ACac6d0f3dbea2d81420510d478e2abb27"
auth_token = "f53eaa2656020a12716bbd300cb29eba"

twilio_number = "+14155238886"  
your_number = "whatsapp:+917869707982"    

client = Client(account_sid, auth_token)

# 🔹 Latest data
latest_data = [0, 0, 0]
latest_rain = 0
latest_status = "OFF"
latest_irrigation = "NO"

# 🔹 Alert control
last_alert_sent = False

# 🔥 =========================
# 🔥 ML MODEL (CSV)
# 🔥 =========================

data = pd.read_csv("data.csv")

X = data[['moisture', 'temperature', 'humidity']]
y = data['Pump Data']

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained using CSV")

def check_rain():
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast?q=Indore&appid=9902c67e295031db242872e0aa5f32f5&units=metric"
        
        response = requests.get(url)
        data = response.json()

        print("FULL API RESPONSE:", data)  # 🔥 debug

        # 🔥 Safe handling
        if data.get("cod") != "200":
            print("API Error:", data.get("message"))
            return 0

        pop = data['list'][0].get('pop', 0)

        print("Rain Probability:", pop)

        return 1 if pop > 0.6 else 0

    except Exception as e:
        print("Rain API Error:", e)
        return 0
# 📩 WhatsApp function
def send_whatsapp(message):
    try:
        client.messages.create(
            body=message,
            from_=twilio_number,
            to=your_number
        )
        print("WhatsApp Sent:")
    except Exception as e:
        import traceback
        print("WhatsApp Error")
        traceback.print_exc()

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

        .box {{
            margin-top: 50px;
            padding: 25px;
            background: white;
            display: inline-block;
            border-radius: 10px;
            box-shadow: 2px 2px 10px gray;
            font-size: 18px;
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

    <div class="header">
        <h2>Shivaji Rao Kadam Group of Institutions</h2>
        <h3>EC Department</h3>
        <h1>Smart Farming Dashboard</h1>
    </div>

    <div class="box">
        <p>Moisture: {moisture}</p>
        <p>Temperature: {temp}</p>
        <p>Humidity: {humidity}</p>
        <p>Rain Chance: {latest_rain*100:.0f}%</p>
        <p>Pump Status: {latest_status}</p>
        <p>Irrigation Required: {latest_irrigation}</p>
    </div>

    <div class="footer">
        <div class="left">
            <b>Created by:</b><br>
            Sheetal Chouhan<br>
            Pramila Yadav<br>
            Mohit Verma
        </div>
        </div>
        

    </body>
    </html>
    """

# 📥 DATA + ML + RAIN + WHATSAPP
@app.route('/data', methods=['GET'])
def receive_data():
    global latest_data, latest_rain, latest_status, latest_irrigation, last_alert_sent

    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        latest_data = [moisture, temp, humidity]

        # 🔥 ML prediction
        result = model.predict([[moisture, temp, humidity]])[0]

        # 🌧️ Rain prediction
        rain = check_rain()
        latest_rain = rain

        # 🔥 FINAL DECISION
        if rain > 0.6:
            decision = 0
        else:
            decision = result

        # 🔥 Status update
        if decision == 1:
            latest_status = "ON"
            latest_irrigation = "YES"
        else:
            latest_status = "OFF"
            latest_irrigation = "NO"

        # 📩 WhatsApp alert
        if decision == 1 and not last_alert_sent:
            send_whatsapp(f"""
Irrigation Required!

Moisture: {moisture}
Temperature: {temp}
Humidity: {humidity}
""")
            last_alert_sent = True

        if decision == 0:
            last_alert_sent = False

        print("Decision:", decision, "Rain:", rain)

        return "ON" if decision == 1 else "OFF"

    except Exception as e:
        print("Error:", e)
        return "Error"

if __name__ == "__main__":
    app.run()
