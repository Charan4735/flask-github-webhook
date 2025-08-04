import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set these securely in your environment
SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]

@app.route("/")
def index():
    return "GitHub webhook listener is running successfully!"

@app.route("/github", methods=["POST"])
def github_webhook():
    event_type = request.headers.get("X-GitHub-Event")
    if event_type != "push":
        return jsonify({"message": "Not a push event"}), 200

    data = request.json
    repo_name = data["repository"]["full_name"]
    pusher_name = data["pusher"]["name"]
    commits = data.get("commits", [])

    summary = f"*{pusher_name}* pushed *{len(commits)}* commit(s):\n"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for commit in commits:
        sha = commit["id"]
        commit_url = f"https://api.github.com/repos/{repo_name}/commits/{sha}"

        resp = requests.get(commit_url, headers=headers)
        if resp.status_code != 200:
            summary += "_Could not fetch commit details from GitHub_\n"
            continue

        commit_data = resp.json()
        message = commit_data["commit"]["message"]
        html_url = commit_data["html_url"]
        files = commit_data.get("files", [])

        modified_files = [f"`{f['filename']}`" for f in files if f["status"] == "modified"]
        added_files = [f"`{f['filename']}`" for f in files if f["status"] == "added"]
        removed_files = [f"`{f['filename']}`" for f in files if f["status"] == "removed"]

        summary += f"\n*Commit:* {message}\n"
        summary += f"🔗 <{html_url}|View Commit>\n"

        if added_files:
            summary += f"➕ Added: {', '.join(added_files)}\n"
        if modified_files:
            summary += f"📝 Modified: {', '.join(modified_files)}\n"
        if removed_files:
            summary += f"❌ Removed: {', '.join(removed_files)}\n"

    # Send to Slack
    slack_data = {"text": summary}
    requests.post(SLACK_WEBHOOK_URL, json=slack_data)

    return jsonify({"message": "Push processed and sent to Slack"}), 200

if __name__ == "__main__":
    app.run(debug=True)
