from flask import Flask, request
import json
import requests
import os

app = Flask(__name__)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # Fetch from Render env vars

@app.route('/github', methods=['POST'])
def github_webhook():
    payload = request.json
    pusher_name = payload.get('pusher', {}).get('name')
    commits = payload.get('commits', [])

    message = f"*{pusher_name}* pushed {len(commits)} commit(s):\n"
    
    for commit in commits:
        message += f"\n*Commit:* {commit['message']}\n"
        message += f"*URL:* {commit['url']}\n"
        added = commit.get('added', [])
        modified = commit.get('modified', [])
        removed = commit.get('removed', [])
        
        if added:
            message += f"➕ *Added:* {', '.join(added)}\n"
        if modified:
            message += f"📝 *Modified:* {', '.join(modified)}\n"
        if removed:
            message += f"❌ *Removed:* {', '.join(removed)}\n"

    # Send to Slack
    if SLACK_WEBHOOK_URL:
        requests.post(SLACK_WEBHOOK_URL, data=json.dumps({'text': message}),
                      headers={'Content-Type': 'application/json'})
    else:
        print("Slack webhook URL not set.")

    return '', 200
