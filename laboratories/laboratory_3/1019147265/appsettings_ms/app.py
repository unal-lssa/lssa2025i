import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "appsettings_service")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)

@app.route('/settings', methods=['GET'])
def get_all_settings():
    settings = Setting.query.all()
    return jsonify([{ "name": s.name, "value": s.value } for s in settings])

def get_setting(name):
    setting = Setting.query.filter_by(name=name).first()
    if setting:
        return jsonify({"name": setting.name, "value": setting.value}), 200
    else:
        return jsonify({"error": "Setting not found"}), 404

@app.route('/settings', methods=['POST'])
def update_setting():
    data = request.json
    name = data.get("name")
    value = data.get("value")

    if not name or value is None:
        return jsonify({"error": "Both 'name' and 'value' are required"}), 400

    setting = Setting.query.filter_by(name=name).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(name=name, value=value)
        db.session.add(setting)

    db.session.commit()
    return jsonify({"message": f"Setting '{name}' updated."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
