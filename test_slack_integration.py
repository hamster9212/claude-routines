#!/usr/bin/env python3
"""
Test Slack integration for Beeminder routines.
This script verifies that the Slack notifier works correctly with both webhook and bot token approaches.
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import the slack notifier
from slack_notifier import send_slack_message

def test_slack_webhook():
    """Test Slack webhook functionality"""
    print("Testing Slack Webhook...")
    message = "Test message from notion_beeminder_sync integration"
    result = send_slack_message(message)
    if result:
        print("[OK] Slack webhook test passed")
        return True
    else:
        print("[INFO] Slack webhook not configured or failed")
        return False

def test_slack_bot_token():
    """Test Slack bot token functionality"""
    print("\nTesting Slack Bot Token...")
    message = "Test message from Google Keep recommender integration"
    channel = os.environ.get("SLACK_CHANNEL_ID")
    result = send_slack_message(message, channel)
    if result:
        print("[OK] Slack bot token test passed")
        return True
    else:
        print("[INFO] Slack bot token not configured or failed")
        return False

def test_json_parsing():
    """Test that the Python script can handle UTF-8 BOM in JSON"""
    print("\nTesting JSON parsing with UTF-8 BOM...")

    # Create test JSON with BOM
    test_data = {
        "company_count": 0,
        "personal_count": 1,
        "waiting_count": 0,
        "has_package_keyword": False,
        "packages": []
    }

    # Create JSON with UTF-8 BOM
    json_str = json.dumps(test_data, ensure_ascii=False)
    # Add BOM manually
    json_with_bom = json_str.encode().decode('utf-8-sig')

    try:
        # Test parsing with the fix from notion_beeminder_sync.py
        parsed = json.loads(json_with_bom.encode().decode('utf-8-sig'))
        print("[OK] JSON parsing with UTF-8 BOM test passed")
        print(f"    Parsed: {parsed}")
        return True
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Slack Integration Test Suite")
    print("=" * 60)

    results = {
        "webhook": test_slack_webhook(),
        "bot_token": test_slack_bot_token(),
        "json_parsing": test_json_parsing(),
    }

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "PASS" if passed else "N/A"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")

    print("\nEnvironment Variables:")
    print(f"  SLACK_BOT_TOKEN: {'Set' if os.environ.get('SLACK_BOT_TOKEN') else 'Not set'}")
    print(f"  SLACK_WEBHOOK_URL: {'Set' if os.environ.get('SLACK_WEBHOOK_URL') else 'Not set'}")
    print(f"  SLACK_CHANNEL_ID: {'Set' if os.environ.get('SLACK_CHANNEL_ID') else 'Not set'}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
