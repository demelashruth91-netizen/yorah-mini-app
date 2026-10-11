
import os
import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = ["1923175721", "1618265543"]
registrations = {}

COURSES = {
    "natural": {
        "name": "Natural",
        "price": 500,
        "link": "https://t.me/+YoC8rVGzq2Y4MWE8",
    },
    "social": {
        "name": "Social",
        "price": 450,
        "link": "https://t.me/+AsBcL0H_QrMwYTVk",
    },
    "aastu": {
        "name": "AASTU / ASTU",
        "price": 500,
        "link": "https://t.me/+6_lWloCF7aIxMWQ8",
    },
}

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = (
        "https://demelashruth91-netizen.github.io"
    )
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

@app.route("/")
def home():
    return "Yorah Academy backend is running!"

@app.route("/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == "OPTIONS":
        return jsonify({"ok": True})

    if not BOT_TOKEN:
        return jsonify({"error": "Backend configuration is incomplete"}), 500

    name = request.form.get("name", "").strip()
    package_key = request.form.get("packageKey", "").strip().lower()
    university = request.form.get("university", "").strip()
    user_id = request.form.get("telegramUserId", "").strip()
    receipt = request.files.get("receipt")

    if not all([name, package_key, university, user_id, receipt]):
        return jsonify({"error": "Please provide all details and the screenshot"}), 400

    if package_key not in COURSES:
        return jsonify({"error": "Invalid package selected"}), 400

    if not user_id.isdigit():
        return jsonify({"error": "Invalid Telegram account"}), 400

    registration_id = uuid.uuid4().hex[:12]
    course = COURSES[package_key]

    registrations[registration_id] = {
        "name": name,
        "package_key": package_key,
        "university": university,
        "user_id": int(user_id),
        "status": "under_review",
    }

    caption = (
        f"PAYMENT REVIEW — {registration_id}\n\n"
        f"Name: {name}\n"
        f"Package: {course['name']}\n"
        f"University: {university}\n"
        f"Amount: {course['price']} ETB"
    )

    keyboard = {
        "inline_keyboard": [[
            {
                "text": "Approve",
                "callback_data": f"approve:{registration_id}",
            },
            {
                "text": "Reject",
                "callback_data": f"reject:{registration_id}",
            },
        ]]
    }

    sent = 0

    for admin_id in ADMIN_IDS:
        try:
            receipt.stream.seek(0)
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": admin_id,
                    "caption": caption,
                    "reply_markup": __import__("json").dumps(keyboard),
                },
                files={
                    "photo": (
                        receipt.filename or "receipt.jpg",
                        receipt.stream,
                        receipt.mimetype or "image/jpeg",
                    )
                },
                timeout=30,
            )
            if response.ok and response.json().get("ok"):
                sent += 1
        except requests.RequestException:
            pass

    if sent == 0:
        registrations.pop(registration_id, None)
        return jsonify({"error": "Could not send screenshot to admins"}), 502

    return jsonify({
        "ok": True,
        "message": "Registration sent for review",
        "registrationId": registration_id,
    })
