import os
import requests
from flask import Flask, request
from openai import OpenAI

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=30
    )


@app.route("/", methods=["GET"])
def home():
    return "Telegram AI Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)

    if not data or "message" not in data:
        return "OK", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text")

    if not text:
        send_telegram_message(
            chat_id,
            "Hozircha faqat matnli xabarlarni qabul qilaman."
        )
        return "OK", 200

    try:
        response = client.responses.create(
            model="gpt-5-mini",
            instructions=(
                "You are a helpful AI assistant inside Telegram. "
                "Reply in the same language as the user. "
                "If the user writes in Uzbek, reply naturally in Uzbek."
            ),
            input=text
        )

        answer = response.output_text

    except Exception:
        answer = "Xatolik yuz berdi. Iltimos, birozdan keyin qayta urinib ko‘ring."

    send_telegram_message(chat_id, answer)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
