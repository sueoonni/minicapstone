from flask import Flask, request, jsonify         #flask:서버본체, request:데이터읽기, jsonify:파이썬데이터를 변환해서 응답할때 사용 
from database import db    #databases.py파일에서 db객체불러옴
import os #주소전달할때 DATABASE_URL 변수 이용해야해서 필요한 헤더

app = Flask(__name__)    #flask가 내부에서 어디서 실행됐는지 자체적으로 파악..

# Render가 db 주소를 flask에 연결하는 과정
db_url = os.environ.get("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db.init_app(app)

# 🔘 제어 신호 테이블 (앱에서 보낸 ON/OFF 상태 저장)
class ControlCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()      #flask가 만든 서버 내에서 DB만들수있게함. 


@app.route("/")
def home(): #기본페이지
    return "🚀 IoT Server is running!" #서버가 정상적으로 켜진 거 확인 메시지


# 🔘 앱 → ON/OFF 제어 명령 수신
@app.route("/control", methods=["POST"])
def add_control_command():
    data = request.get_json()
    device = data.get("device")
    state = data.get("state")

    if not device or not state:
        return jsonify({"error": "Missing device or state"}), 400

    cmd = ControlCommand(device=device, state=state)
    db.session.add(cmd)
    db.session.commit()

    return jsonify({"message": f"{device} set to {state}"}), 200

# 🔘 최신 제어 상태 조회
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
