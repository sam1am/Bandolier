from slack_sdk import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

# This `app` represents your existing Flask app
app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(
    os.getenv("SLACK_SIGNING_SECRET"), "/slack/events", app
)

# Create a client instance
slack_web_client = WebClient(token=os.getenv("SLACK_TOKEN"))


# When a message is sent in the channel, this event is triggered
@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    # Fetch the channel name using slack_web_client
    response = slack_web_client.conversations_info(channel=channel_id)
    channel_name = response["channel"]["name"]

    # Fetch the username using slack_web_client
    response = slack_web_client.users_info(user=user_id)
    user_name = response["user"]["name"]

    # Make sure the logs directory exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # We will use channel name as a substitute for group name
    group_dir = os.path.join("logs", channel_name)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    log_filename = os.path.join(group_dir, f"{channel_name}.txt")

    # Write the log to a file
    with open(log_filename, "a") as log_file:
        log_file.write(f"User {user_name} in channel {channel_name} says: {text}\n")


if __name__ == "__main__":
    app.run(port=3000)
