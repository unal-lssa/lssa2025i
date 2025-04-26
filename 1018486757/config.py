import os
from functools import wraps
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import ast 

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
CERTIFICATE_DB = os.getenv("CERTIFICATE_DB")
CERTIFICATE_MS = os.getenv("CERTIFICATE_MS")
CERTIFICATE_PAY = os.getenv("CERTIFICATE_PAY")
AUTHORIZED_IP = os.getenv("AUTHORIZED_IP")
USERS = {
    "user1": os.getenv("password_user1"),
    "admin": os.getenv("password_admin")
}

def limit_exposure(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip != AUTHORIZED_IP:
            return jsonify({'message': 'Forbidden: Unauthorized IP'}), 403
        return f(*args, **kwargs)

    return decorated_function
