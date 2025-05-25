import os
import requests

TORN_API_KEY = os.getenv("TORN_API_KEY")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
TORN_USER_ID = os.getenv("TORN_USER_ID", "1")

def get_latest_thread():
    url = f"https://api.torn.com/v2/user/{TORN_USER_ID}/forumthreads?limit=1"
    headers = {
        "Authorization": f"ApiKey {TORN_API_KEY}",
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    threads = response.json().get("forumThreads", [])
    return threads[0] if threads else None

def get_first_post(thread_id):
    url = f"https://api.torn.com/v2/forum/{thread_id}/posts?striptags=true"
    headers = {
        "Authorization": f"ApiKey {TORN_API_KEY}",
        "accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    posts = response.json().get("posts", [])
    return posts[0]["content"] if posts else None

def send_to_discord(title, content, thread_id):
    data = {
        "content": f"**{title}**\nhttps://www.torn.com/forums.php#/p={thread_id}\n\n```{content[:1900]}```"
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    response.raise_for_status()

def main():
    latest = get_latest_thread()
    if not latest:
        print("No latest thread found")
        return

    thread_id = str(latest["id"])
    content = get_first_post(thread_id)
    if not content:
        print("No content found in latest thread")
        return

    send_to_discord(latest["title"], content, thread_id)
    print(f"Sent latest post from thread {thread_id} to Discord!")

if __name__ == "__main__":
    main()
