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
y = data['Pump Data']

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained using CSV ✅")
# rain function
def check_rain():
    try:
        url ="https://api.openweathermap.org/data/2.5/forecast?q=Indore&appid=dbf4091609c1594c6f912ff35c6b1bcd&units=metric"
        data = requests.get(url).json()
        pop = data['list'][0]['pop']
        print("rain probability:", pop)
        if pop > 0.6:
            return 1
        else:
            return 0
        except:
            print("rain API error")
            return 0
#dashboard decoration
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

        .header h2 {{
            margin: 5px;
            font-size: 18px;
        }}

        .header h3 {{
            margin: 5px;
            font-size: 14px;
            font-weight: normal;
        }}

        .box {{
            margin-top: 60px;
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

    <!-- 🔝 Header -->
    <div class="header">
        <h2>Shivaji Rao Kadam Group of Institutions</h2>
        <h3>Department of Electronics & Communication (EC)</h3>
        <h1>Smart Farming Dashboard 🌱</h1>
    </div>

    <!-- 📊 Data -->
    <div class="box">
        <p>🌱 Moisture: {moisture}</p>
        <p>🌡️ Temperature: {temp}</p>
        <p>💧 Humidity: {humidity}</p>
    </div>

    <!-- 👇 Footer -->
    <div class="footer">
        <div class="left">
            <b>Created by:</b><br>
            Sheetal Chouhan<br>
            Pramila Yadav<br>
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
# 📥 DATA + ML + rain + SMS
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
        
        #rain prediction
        rain = check_rain()
        
        # final decision
        if rain == 1:
            decision = 0
        else:
            decision = result

        # 🔥 SMS only when irrigation  needed
        if decision == 1 and not last_alert_sent:
            send_sms(f"""
🚨 mitti sukh gyi hai pani do!

🌱 Moisture: {moisture:.1f}%
🌡 Temp: {temp:.1f}°C
💧 Humidity: {humidity:.1f}%
""")
            last_alert_sent = True

        if decision == 0:
            last_alert_sent = False

        print("Decision:", decision, "Rain:", rain)

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
