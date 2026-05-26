#!/usr/bin/env python3
"""
Slack Notifier Helper
Sends messages to Slack via webhook or bot token.

Usage:
  python slack_notifier.py '<message>' [channel]

Environment variables:
  SLACK_BOT_TOKEN: Bot token for app (e.g., xoxb-...)
  SLACK_WEBHOOK_URL: Webhook URL for direct posting
  SLACK_CHANNEL_ID: Default channel ID (if using bot token)
"""

import os
import sys
import json
import requests
from typing import Optional

def send_slack_message(
    message: str,
    channel_id: Optional[str] = None
) -> bool:
    """Send message to Slack via webhook or bot token"""

    # Try webhook first
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        try:
            payload = {"text": message}
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print(f"[OK] Slack webhook sent: {message[:50]}...")
                return True
            else:
                print(f"[ERROR] Webhook returned {response.status_code}: {response.text}")
                return False
        except Exception as e:
            print(f"[ERROR] Webhook failed: {e}")
            return False

    # Try bot token
    bot_token = os.environ.get("SLACK_BOT_TOKEN")
    if bot_token and (channel_id or os.environ.get("SLACK_CHANNEL_ID")):
        try:
            channel = channel_id or os.environ.get("SLACK_CHANNEL_ID")
            headers = {"Authorization": f"Bearer {bot_token}"}
            payload = {"channel": channel, "text": message}
            response = requests.post(
                "https://slack.com/api/chat.postMessage",
                json=payload,
                headers=headers,
                timeout=10
            )
            data = response.json()
            if data.get("ok"):
                print(f"[OK] Slack bot sent: {message[:50]}...")
                return True
            else:
                print(f"[ERROR] Bot API error: {data.get('error')}")
                return False
        except Exception as e:
            print(f"[ERROR] Bot token failed: {e}")
            return False

    print("[WARNING] No Slack credentials configured (SLACK_WEBHOOK_URL or SLACK_BOT_TOKEN)")
    return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Usage: python slack_notifier.py '<message>' [channel_id]")
        sys.exit(1)

    message = sys.argv[1]
    channel = sys.argv[2] if len(sys.argv) > 2 else None

    success = send_slack_message(message, channel)
    sys.exit(0 if success else 1)
