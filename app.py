import os
import requests
from flask import Flask, request
from github_webhook import Webhook

app = Flask(__name__)
webhook = Webhook(app)

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

@webhook.hook("/github")
def on_push(data):
    repo_name = data["repository"]["full_name"]
    pusher_name = data["pusher"]["name"]
    commits = data["commits"]
 
    message = f"*New push to* `{repo_name}` by *{pusher_name}*:\n\n"

    for commit in commits:
        commit_id = commit["id"][:7]
        commit_msg = commit["message"]
        author = commit["author"]["name"]
        url = commit["url"].replace("api.", "").replace("repos/", "").replace("commits", "commit")

        # Fetch diff using GitHub API
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3.diff"
        }
        diff_resp = requests.get(commit["url"], headers=headers)
        if diff_resp.status_code == 200:
            diff_text = diff_resp.text[:1000]  # Limit characters to avoid Slack overflow
        else:
            diff_text = "_Could not fetch diff_"

        message += f":bookmark_tabs: *Commit:* <{url}|`{commit_id}`> by `{author}`\n"
        message += f"> {commit_msg}\n"
        message += f"```{diff_text}```\n"

    send_to_slack(message)

def send_to_slack(msg):
    requests.post(SLACK_WEBHOOK_URL, json={"text": msg})

@app.route("/")
def index():
    return "GitHub webhook listener is running successfully in web"
