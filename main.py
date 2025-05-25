from flask import Flask
import os
import requests

app = Flask(__name__)

TORN_API_KEY = os.getenv("TORN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TORN_USER_ID = os.getenv("TORN_USER_ID", "1")
LAST_POST_FILE = "last_post_id.txt"

def get_latest_thread():
    url = f"https://api.torn.com/v2/user/{TORN_USER_ID}/forumthreads?limit=1"
    headers = {
        "Authorization": f"ApiKey {TORN_API_KEY}",
        "accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        threads = response.json().get("forumThreads", [])
        return threads[0] if threads else None
    except Exception as e:
        print("Error fetching thread:", e)
        return None

def get_first_post(thread_id):
    url = f"https://api.torn.com/v2/forum/{thread_id}/posts?striptags=true"
    headers = {
        "Authorization": f"ApiKey {TORN_API_KEY}",
        "accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        posts = response.json().get("posts", [])
        return posts[0]["content"] if posts else None
    except Exception as e:
        print("Error fetching post:", e)
        return None

def send_to_discord(title, content, thread_id):
    data = {
        "content": f"**{title}**\nhttps://www.torn.com/forums.php#/p={thread_id}\n\n```{content[:1900]}```"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"Sent alert for thread {thread_id}")
    except Exception as e:
        print("Error sending to Discord:", e)

def read_last_post_id():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r") as f:
            return f.read().strip()
    return None

def write_last_post_id(post_id):
    with open(LAST_POST_FILE, "w") as f:
        f.write(str(post_id))

def run_bot():
    latest = get_latest_thread()
    if not latest:
        return "No thread found"

    thread_id = str(latest["id"])
    last_id = read_last_post_id()

    if thread_id != last_id:
        content = get_first_post(thread_id)
        if content:
            send_to_discord(latest["title"], content, thread_id)
            write_last_post_id(thread_id)
            return f"New thread posted: {thread_id}"
        else:
            return "No content found"
    return "Already posted"

@app.route("/")
def trigger():
    result = run_bot()
    return result or "Nothing happened"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
