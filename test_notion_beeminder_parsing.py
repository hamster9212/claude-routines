#!/usr/bin/env python3
"""
Test the notion_beeminder_sync.py JSON parsing with UTF-8 BOM fix.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_json_parsing():
    """Test JSON parsing with the fixed notion_beeminder_sync.py"""
    print("Testing notion_beeminder_sync.py JSON Parsing with UTF-8 BOM")
    print("=" * 60)

    test_data = {
        "company_count": 0,
        "personal_count": 1,
        "waiting_count": 0,
        "has_package_keyword": False,
        "packages": []
    }

    # Create JSON string
    json_str = json.dumps(test_data, ensure_ascii=False)

    # Test 1: Normal JSON (no BOM)
    print("\nTest 1: Normal JSON (no BOM)")
    result = subprocess.run(
        ["python", "notion_beeminder_sync.py", json_str],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )

    if "RESULT_JSON:" in result.stdout:
        print("[PASS] Normal JSON parsing works")
        # Extract and parse the result
        for line in result.stdout.split('\n'):
            if line.startswith("RESULT_JSON:"):
                result_json = line.replace("RESULT_JSON:", "")
                parsed = json.loads(result_json)
                print(f"  Result: condition1_pass={parsed.get('condition1_pass')}")
                print(f"          slack_message='{parsed.get('slack_message')}'")
                break
    else:
        print("[FAIL] Normal JSON parsing failed")
        print(f"stdout: {result.stdout[:200]}")
        print(f"stderr: {result.stderr[:200]}")
        return False

    # Test 2: JSON with UTF-8 BOM
    print("\nTest 2: JSON with UTF-8 BOM")
    # Add BOM
    json_with_bom = json_str.encode().decode('utf-8-sig')

    result = subprocess.run(
        ["python", "notion_beeminder_sync.py", json_with_bom],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )

    if "RESULT_JSON:" in result.stdout:
        print("[PASS] JSON with UTF-8 BOM parsing works")
        for line in result.stdout.split('\n'):
            if line.startswith("RESULT_JSON:"):
                result_json = line.replace("RESULT_JSON:", "")
                parsed = json.loads(result_json)
                print(f"  Result: condition1_pass={parsed.get('condition1_pass')}")
                print(f"          slack_message='{parsed.get('slack_message')}'")
                break
    else:
        print("[FAIL] JSON with UTF-8 BOM parsing failed")
        print(f"stdout: {result.stdout[:200]}")
        print(f"stderr: {result.stderr[:200]}")
        return False

    # Test 3: Verify slack_message is in result
    print("\nTest 3: Verify slack_message field in result")
    test_data2 = {
        "company_count": 1,
        "personal_count": 0,
        "waiting_count": 0,
        "has_package_keyword": False,
        "packages": []
    }
    json_str2 = json.dumps(test_data2, ensure_ascii=False)

    result = subprocess.run(
        ["python", "notion_beeminder_sync.py", json_str2],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )

    if "RESULT_JSON:" in result.stdout:
        for line in result.stdout.split('\n'):
            if line.startswith("RESULT_JSON:"):
                result_json = line.replace("RESULT_JSON:", "")
                parsed = json.loads(result_json)
                if "slack_message" in parsed:
                    print(f"[PASS] slack_message field is present")
                    print(f"  Message: '{parsed.get('slack_message')}'")
                else:
                    print("[FAIL] slack_message field is missing")
                    return False
                break
    else:
        print("[FAIL] Script execution failed")
        return False

    print("\n" + "=" * 60)
    print("All tests passed!")
    return True

if __name__ == "__main__":
    success = test_json_parsing()
    sys.exit(0 if success else 1)
