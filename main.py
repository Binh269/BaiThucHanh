
import paho.mqtt.client as mqtt
from flask import Flask, render_template, request, jsonify
import threading
from datetime import datetime

# MQTT Configuration
BROKER_ADDRESS = "192.168.0.100"  # Địa chỉ Raspberry Pi
TOPIC = "CamBien"  # Tên topic MQTT

# Data storage for received messages
data_received = {"time": "Chưa có dữ liệu", "data": "Chưa có dữ liệu","temperature":"Chưa có dữ liệu","humidity":"Không có dữ liệu"}

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT Broker with code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global data_received
    try:
        payload = msg.payload.decode()
        print(f"Received message: {payload}")
        # Giả sử payload là JSON: {"time": ..., "data": ...}
        payload_data = eval(payload)  # Hoặc dùng json.loads nếu cần
        data_received["time"] = payload_data.get("time", "N/A")
        data_received["data"] = payload_data.get("data", "N/A")
        data_received["temperature"] = payload_data.get("temperature", "N/A")
        data_received["humidity"] = payload_data.get("humidity", "N/A")
    except Exception as e:
        print(f"Error decoding message: {e}")

# MQTT Client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER_ADDRESS)

# Flask Application
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", data=data_received)

@app.route("/send", methods=["POST"])
def send_data():
    user_data = request.form.get("user_data")
    payload = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": user_data
    }
    mqtt_client.publish(TOPIC, str(payload))  # Gửi dữ liệu lên MQTT
    return jsonify({"message": "Dữ liệu đã được gửi!", "sent_data": payload})

# Run Flask and MQTT in parallel
if __name__ == "__main__":
    threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
