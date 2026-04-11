from flask import Flask, request, jsonify, render_template
from sklearn.tree import DecisionTreeClassifier
import pandas as pd
import requests
from twilio.rest import Client

app = Flask(__name__)

# 🔹 Twilio credentials
account_sid = "ACac6d0f3dbea2d81420510d478e2abb27"
auth_token = "43a111cb4507027e5b5b9500c856b477"

twilio_number = "whatsapp:+14155238886"
your_number = "whatsapp:+917869707982"

client = Client(account_sid, auth_token)

# 🔹 Latest data storage
latest_data = [0, 0, 0]  # moisture, temp, humidity
latest_rain = 0
latest_status = "OFF"
latest_irrigation = "NO"

last_alert_sent = False

# 🔥 ML MODEL
data = pd.read_csv("data.csv")

X = data[['moisture', 'temperature', 'humidity']]
y = data['Pump Data']

model = DecisionTreeClassifier()
model.fit(X, y)

print("Model trained")

# 🌧 Rain API
def check_rain():
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast?q=Indore&appid=9902c67e295031db242872e0aa5f32f5&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            return 0

        pop = data['list'][0].get('pop', 0)
        return 1 if pop > 0.6 else 0

    except:
        return 0

# 📩 WhatsApp
def send_whatsapp(msg):
    try:
        client.messages.create(
            body=msg,
            from_=twilio_number,
            to=your_number
        )
    except:
        print("WhatsApp error")

# 🌐 DASHBOARD PAGE
@app.route("/")
def dashboard():
    return render_template("index.html")


# 📊 LIVE DATA API (FOR CHART)
@app.route("/chart-data")
def chart_data():
    moisture, temp, humidity = latest_data

    return jsonify({
        "labels": ["Moisture", "Temperature", "Humidity"],
        "values": [moisture, temp, humidity],
        "status": latest_status,
        "irrigation": latest_irrigation,
        "rain": latest_rain
    })


# 📥 SENSOR INPUT + ML + LOGIC
@app.route('/data')
def receive_data():
    global latest_data, latest_rain, latest_status, latest_irrigation, last_alert_sent

    try:
        moisture = float(request.args.get('moisture'))
        temp = float(request.args.get('temperature'))
        humidity = float(request.args.get('humidity'))

        latest_data = [moisture, temp, humidity]

        # ML prediction
        result = model.predict([[moisture, temp, humidity]])[0]

        # Rain
        rain = check_rain()
        latest_rain = rain

        decision = 0 if rain else result

        if decision == 1:
            latest_status = "ON"
            latest_irrigation = "YES"
        else:
            latest_status = "OFF"
            latest_irrigation = "NO"

        # WhatsApp alert
        if decision == 1 and not last_alert_sent:
            send_whatsapp(f"Irrigation ON!\nMoisture:{moisture}\nTemp:{temp}\nHumidity:{humidity}")
            last_alert_sent = True

        if decision == 0:
            last_alert_sent = False

        return "OK"

    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
