from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

@app.route('/github', methods=['POST'])
def github_webhook():
    data = request.json
    repo = data['repository']['full_name']
    pusher = data['pusher']['name']
    commits = data['commits']
    commit_messages = "\n".join([f"- {c['message']}" for c in commits])

    slack_msg = {
        "text": f"📦 *{repo}* was updated by *{pusher}*:\n{commit_messages}"
    }
    requests.post(SLACK_WEBHOOK_URL, json=slack_msg)
    return jsonify({"status": "Message sent to Slack application"}), 200
