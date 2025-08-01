from flask import Flask, request
import requests

app = Flask(__name__)

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/your/.../..."  # Replace with your actual Slack webhook

@app.route("/github", methods=["POST"])
def github_webhook():
    payload = request.json
    if payload:
        repo = payload["repository"]["full_name"]
        pusher = payload["pusher"]["name"]
        msg = f"📦 New push to *{repo}* by *{pusher}*."

        # Send to Slack
        requests.post(SLACK_WEBHOOK_URL, json={"text": msg})

        print("✅ Message sent to Slack.")
        return "Message sent to Slack", 200
    return "No payload", 400
