from flask import Flask, redirect, request
import requests
import json

app = Flask(__name__)

BLUE_SERVER = "http://localhost:5001"
GREEN_SERVER = "http://localhost:5002"

def get_server_status():
    try:
        response = requests.get(f"{BLUE_SERVER}/api/status")
        return response.json()
    except requests.exceptions.ConnectionError:
        return None

@app.route("/")
def index():
    status = get_server_status()
    if status and "blue" in status and "sessions" in status["blue"] and len(status["blue"]["sessions"]) < 3:
        return redirect(BLUE_SERVER)
    else:
        return redirect(GREEN_SERVER)

if __name__ == "__main__":
    app.run(port=5000)