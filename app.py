from flask import Flask, request, jsonify
from database import db
from datetime import datetime
import os

app = Flask(__name__)

# 🧩 Render의 DB URL 연결
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# 🔘 제어 신호 테이블 (앱 → 서버)
class ControlCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)


# 🌡️ 온습도 데이터 테이블 (ESP32 → 서버)
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Float, nullable=False)
    hum = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)


# DB 생성
with app.app_context():
    db.create_all()


# 기본 페이지
@app.route("/")
def home():
    return "🚀 IoT Server is running!"


# 🔘 앱 → 서버: ON/OFF 제어 명령 수신
@app.route("/control", methods=["POST"])
def add_control_command():
    data = request.get_json()
    device = data.get("device")
    state = data.get("state")

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received Command: {device} set to {state}")

    if not device or not state:
        return jsonify({"error": "Missing device or state"}), 400

    cmd = ControlCommand(device=device, state=state)
    db.session.add(cmd)
    db.session.commit()

    return jsonify({"message": f"{device} set to {state}"}), 200


# 🌡️ ESP32 → 서버: 온습도 데이터 수신
@app.route("/add", methods=["POST"])
def add_sensor_data():
    data = request.get_json()
    temp = data.get("temp")
    hum = data.get("hum")

    if temp is None or hum is None:
        return jsonify({"error": "Missing temperature or humidity"}), 400

    record = SensorData(temp=temp, hum=hum)
    db.session.add(record)
    db.session.commit()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🌡️ Data received → Temp: {temp}°C / Humidity: {hum}%")
    
    return jsonify({"message": "Sensor data stored!"}), 200


# 🌡️ 최신 온습도 데이터 조회
@app.route("/latest", methods=["GET"])
def get_latest_sensor_data():
    record = SensorData.query.order_by(SensorData.id.desc()).first()
    if record:
        return jsonify({
            "temp": record.temp,
            "hum": record.hum,
            "time": record.time.isoformat()
        })
    else:
        return jsonify({"message": "No data yet."}), 404


# 🔘 최신 제어 상태 조회 (ESP32 → 서버)
@app.route("/control/latest", methods=["GET"])
def get_latest_control():
    record = ControlCommand.query.order_by(ControlCommand.id.desc()).first()
    if record:
        return jsonify({
            "device": record.device,
            "state": record.state,
            "time": record.time.isoformat()
        })
    else:
        return jsonify({"message": "No control commands yet."}), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
