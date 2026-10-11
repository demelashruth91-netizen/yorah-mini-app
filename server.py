
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = ["1923175721", "1618265543"]

@app.route("/")
def home():
    return "Yorah Academy backend is running!"

@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        response = jsonify({"ok": True})
        response.headers["Access-Control-Allow-Origin"] = "https://demelashruth91-netizen.github.io"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response

    if not BOT_TOKEN:
        return jsonify({"error": "Backend configuration is incomplete"}), 500

    name = request.form.get("name", "").strip()
    package = request.form.get("packageKey", "").strip()
    university = request.form.get("university", "").strip()
    receipt = request.files.get("receipt")

    if not all([name, package, university, receipt]):
        return jsonify({"error": "Please provide all registration details and the receipt"}), 400

    caption = (
        "New Yorah Academy registration\n"
        f"Name: {name}\n"
        f"Package: {package}\n"
        f"University: {university}"
    )

    results = []
    for admin_id in ADMIN_IDS:
        try:
            receipt.stream.seek(0)
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": admin_id, "caption": caption},
                files={"photo": (receipt.filename or "receipt.jpg", receipt.stream, receipt.mimetype or "image/jpeg")},
                timeout=30,
            )
            results.append(response.ok and response.json().get("ok", False))
        except requests.RequestException:
            results.append(False)

    if not any(results):
        return jsonify({"error": "Could not send the registration to an admin"}), 502

    response = jsonify({"ok": True, "message": "Registration sent for review"})
    response.headers["Access-Control-Allow-Origin"] = "https://demelashruth91-netizen.github.io"
    return response
