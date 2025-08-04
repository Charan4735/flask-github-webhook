import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set your environment variables before running this
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

@app.route("/")
def index():
    return "GitHub webhook listener is running successfully!"

@app.route("/github", methods=["POST"])
def github_webhook():
    # Check for GitHub push event
    event_type = request.headers.get("X-GitHub-Event")
    if event_type != "push":
        return jsonify({"message": "Not a push event"}), 200

    data = request.json
    repo_name = data["repository"]["full_name"]
    pusher_name = data["pusher"]["name"]
    commits = data.get("commits", [])

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }

    for commit in commits:
        commit_url = commit["url"]
        commit_msg = commit["message"]
        commit_sha = commit["id"][:7]

        # Get the code diff from GitHub API
        diff_resp = requests.get(commit_url, headers=headers)
        if diff_resp.status_code == 200:
            diff_text = diff_resp.text[:1000]  # First 1000 chars to avoid flooding
        else:
            diff_text = "_Could not fetch diff from GitHub_"

        # Prepare message to send to Slack
        slack_message = {
            "text": f"*{repo_name}* — New push by *{pusher_name}*\n"
                    f"*Commit:* `{commit_sha}`\n"
                    f"> {commit_msg}\n"
                    f"```diff\n{diff_text}\n```"
        }

        requests.post(SLACK_WEBHOOK_URL, json=slack_message)

    return jsonify({"message": "Push processed"}), 200

if __name__ == "__main__":
    app.run(debug=True)
