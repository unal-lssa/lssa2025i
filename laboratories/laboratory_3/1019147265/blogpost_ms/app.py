from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "blogpost_service")

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "description": p.description,
            "owner": p.owner,
            "date": p.date.isoformat()
        }
        for p in posts
    ])

@app.route('/posts', methods=['POST'])
def create_post():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    owner = data.get('owner')

    if not title or not description or not owner:
        return jsonify({"error": "title, description, and owner are required"}), 400

    post = Post(title=title, description=description, owner=owner)
    db.session.add(post)
    db.session.commit()

    return jsonify({"message": "Post created"}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
