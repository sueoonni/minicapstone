from flask import Flask, request, jsonify         #flask:서버본체, request:데이터읽기, jsonify:파이썬데이터를 변환해서 응답할때 사용 
from database import db    #databases.py파일에서 db객체불러옴
import os #주소전달할때 DATABASE_URL 변수 이용해야해서 필요한 헤더

app = Flask(__name__)    #flask가 내부에서 어디서 실행됐는지 자체적으로 파악..

# Render가 db 주소를 flask에 연결하는 과정
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db.init_app(app)

# 간단한 테이블 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()      #flask가 만든 서버 내에서 DB만들수있게함. 

# 온습도 데이터테이블
class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temp = db.Column(db.Float, nullable=False)
    hum = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

# 🔘 제어 신호 테이블 (앱에서 보낸 ON/OFF 상태 저장)
class ControlCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(10), nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)



@app.route("/")
def home(): #기본페이지
    return "🚀 Flask + server is running!" 서버가 정상적으로 켜진 거 확인 메시지. Render에서 접속했을 때 이 문장 떠야함. 

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = [{"id": u.id, "name": u.name} for u in users]
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

