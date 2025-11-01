from flask import Flask, request, jsonify
from database import db
import os

app = Flask(__name__)

# Render가 자동으로 설정하는 환경변수 사용 (PostgreSQL 연결)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 간단한 테이블 정의
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return "🚀 Suyeoni's Flask + PostgreSQL server is running!"

@app.route("/add", methods=["POST"])
def add_user():
    data = request.get_json()
    new_user = User(name=data["name"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User added!"})

@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    result = [{"id": u.id, "name": u.name} for u in users]
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

