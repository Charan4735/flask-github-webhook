import os
import requests
from flask import Flask
from github_webhook import Webhook

app = Flask(__name__)
webhook = Webhook(app, endpoint="/github")

# Environment variables
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

@webhook.hook()
def on_push(data):
    repo_name = data["repository"]["full_name"]
    pusher_name = data["pusher"]["name"]
    commits = data["commits"]
    
    message = f"{pusher_name} pushed {len(commits)} commit(s):\n"

    for commit in commits:
        commit_msg = commit["message"]
        commit_url = commit["url"].replace("api.", "").replace("repos/", "").replace("commits", "commit")

        message += f"*Commit:* {commit_msg}\n"
        message += f"*URL:* <{commit_url}>\n"

        # File changes
        if commit.get("added"):
            for f in commit["added"]:
                message += f":heavy_plus_sign: Added: `{f}`\n"
        if commit.get("removed"):
            for f in commit["removed"]:
                message += f":x: Removed: `{f}`\n"
        if commit.get("modified"):
            for f in commit["modified"]:
                message += f":memo: Modified: `{f}`\n"

        message += "\n"

    send_to_slack(message)

def send_to_slack(msg):
    requests.post(SLACK_WEBHOOK_URL, json={"text": msg})

@app.route("/")
def index():
    return "GitHub webhook listener is running successfully"
