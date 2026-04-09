from flask import Flask, request
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import requests

app = Flask(__name__)

# 🔹 Latest data
latest_data = [0, 0, 0]
latest_rain = 0

# 🔥 ML MODEL (CSV)
data = pd.read_csv("data.csv")

X = data[['moisture', 'temperature', 'humidity']]
y = data['pump data']

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained using CSV ✅")

# 🌧️ Rain function
def check_rain():
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast?q=Indore&appid=YOUR_API_KEY&units=metric"
        
        weather_data = requests.get(url).json()
        pop = weather_data['list'][0]['pop']   # rain probability

        print("Rain:", pop)
        return pop

    except Exception as e:
        print("Rain API Error:", e)
        return 0

# 🌐 DASHBOARD
@app.route('/')
def dashboard():
    moisture, temp, humidity = latest_data
    rain = latest_rain

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
    </style>
    </head>

    <body>

    <div class="header">
        <h2>Shivaji Rao Kadam Group of Institutions</h2>
        <h3>EC Department</h3>
        <h1>Smart Farming Dashboard 🌱</h1>
    </div>

    <div class="box">
        <p>🌱 Moisture: {moisture}</p>
        <p>🌡️ Temperature: {temp}</p>
        <p>💧 Humidity: {humidity}</p>
        <p>🌧️ Rain Chance: {rain*100:.0f}%</p>
    </div>

    <div class="footer">
        <div>
            <b>Created by:</b><br>
            Sheetal Chouhan<br>
            Pramila Yadav<br>
            Mohit Verma
        </div>

    </body>
    </html>
    """

# 📥 DATA + ML + RAIN
@app.route('/data', methods=['GET'])
def receive_data():
    global latest_data, latest_rain

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
            decision = 0   # rain aa raha → OFF
        else:
            decision = result

        print("Decision:", decision, "Rain:", rain)

        return "ON" if decision == 1 else "OFF"

    except Exception as e:
        print("Error:", e)
        return "Error"

if __name__ == "__main__":
    app.run()
