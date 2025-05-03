# ms_auth Service
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello from ms_auth!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8003)
