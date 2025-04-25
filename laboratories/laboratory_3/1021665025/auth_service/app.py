from flask import Flask, request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from models import Base, User, Role # Import models
import os
import bcrypt # For password hashing
import jwt 
import datetime # For JWT expiry

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/auth_db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# For this example, we'll use an environment variable or a default
SECRET_KEY = os.environ.get('SECRET_KEY', 'b36e068c3e28c07a152766ebddfbb6a882a767d29edce9068c79c90038f2b516d2401fa96110a316843f00bc1cf3cac2be0f590514d8043dfe5919531a1754f2cde9714a68468674a887bed68ca7c2595b4d1c30a37134e056d0628d2eb417ae3e4af702bd9b1d8db675d62e744bc74f7a847094384f62e8f629dfb06d36f815b1d699389e0064cb41f45c85551e9c268d8437c7b6cdd6a750f13899173b85e8ca25fc242be57d0fea69f06819ae99be9483fedda47ea8a7831f920f0d98ec1a1a7f3057ec639683a4330fff85248a3704c6f176f92873774fc81dd14ea4808cec94714c392197000b84351a2198972efc492e92b898c68cbc48b747ec584ecf')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper function to get a database session
def current_db():
    return next(get_db())

@app.route('/auth/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role_names = data.get('roles', ['user']) # Default role is 'user'

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    db = current_db()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return jsonify({'message': 'User already exists'}), 409

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Create new user
        new_user = User(username=username, password_hash=hashed_password.decode('utf-8'))

        # Assign roles
        for role_name in role_names:
            role = db.query(Role).filter(Role.name == role_name).first()
            if role:
                new_user.roles.append(role)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return jsonify({'message': 'User registered successfully', 'user_id': new_user.id}), 201

    except IntegrityError:
        db.rollback()
        return jsonify({'message': 'User already exists (Integrity Error)'}), 409
    except Exception as e:
        db.rollback()
        return jsonify({'message': 'An error occurred during registration', 'error': str(e)}), 500
    finally:
        db.close()


@app.route('/auth/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    db = current_db()
    try:
        user = db.query(User).filter(User.username == username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Authentication successful
            # Generate JWT token (or delegate to API Gateway)
            # Include roles in the token payload
            roles = [role.name for role in user.roles]
            token_payload = {
                'user_id': user.id,
                'username': user.username,
                'roles': roles,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Token expiry
            }
            token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

            return jsonify({'token': token})
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'message': 'An error occurred during login', 'error': str(e)}), 500
    finally:
        db.close()

# Endpoint to get user's roles (useful for API Gateway authorization)
@app.route('/auth/user/<int:user_id>/roles', methods=['GET'])
def get_user_roles(user_id):
    db = current_db()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404

        roles = [role.name for role in user.roles]
        return jsonify({'user_id': user.id, 'username': user.username, 'roles': roles})

    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    finally:
        db.close()

# Example endpoint to get a list of all roles
@app.route('/auth/roles', methods=['GET'])
def get_all_roles():
    db = current_db()
    try:
        roles = db.query(Role).all()
        roles_list = [{"id": r.id, "name": r.name} for r in roles]
        return jsonify(roles_list)
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    finally:
        db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)