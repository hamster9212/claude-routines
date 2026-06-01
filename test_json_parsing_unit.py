#!/usr/bin/env python3
"""
Unit test for JSON parsing with UTF-8 BOM fix.
This directly tests the parsing logic without needing environment variables.
"""

import json
import sys

def test_json_parsing_with_bom():
    """Test that JSON can be parsed after UTF-8 BOM handling"""
    print("Unit Test: JSON Parsing with UTF-8 BOM")
    print("=" * 60)

    test_data = {
        "company_count": 0,
        "personal_count": 1,
        "waiting_count": 0,
        "has_package_keyword": False,
        "packages": []
    }

    # Test 1: Normal JSON (no BOM)
    print("\nTest 1: Normal JSON (no BOM)")
    json_str = json.dumps(test_data, ensure_ascii=False)
    try:
        # This is how the original code parsed JSON
        data = json.loads(json_str)
        print("[PASS] Normal JSON parsing works")
        print(f"  Parsed: {data}")
    except json.JSONDecodeError as e:
        print(f"[FAIL] Normal JSON parsing failed: {e}")
        return False

    # Test 2: JSON with UTF-8 BOM (simulating what PowerShell might do)
    print("\nTest 2: JSON with UTF-8 BOM")
    json_str = json.dumps(test_data, ensure_ascii=False)
    # Add BOM prefix (UTF-8 BOM is ﻿)
    json_with_bom = '﻿' + json_str

    try:
        # This would fail with the old code:
        # data = json.loads(json_with_bom)
        # But succeeds with the new code:
        data_old_way = json.loads(json_with_bom)
        print("[INFO] Direct JSON parsing with BOM character works (unexpected)")
    except json.JSONDecodeError as e:
        print(f"[INFO] Direct JSON parsing with BOM fails as expected: {e}")

    # This is the FIX - encode then decode with utf-8-sig
    try:
        data = json.loads(json_with_bom.encode().decode('utf-8-sig'))
        print("[PASS] JSON with UTF-8 BOM parsing works (with fix)")
        print(f"  Parsed: {data}")
    except json.JSONDecodeError as e:
        print(f"[FAIL] JSON with UTF-8 BOM parsing failed: {e}")
        return False

    # Test 3: Test with PowerShell-like JSON from command line
    print("\nTest 3: PowerShell-generated JSON scenario")
    # Simulate what PowerShell ConvertTo-Json might pass
    ps_json = '{"company_count":0,"personal_count":1,"waiting_count":0,"has_package_keyword":false,"packages":[]}'

    try:
        # Using the fix from the script
        data = json.loads(ps_json.encode().decode('utf-8-sig'))
        print("[PASS] PowerShell JSON scenario works")
        print(f"  Parsed: {data}")
        if "slack_message" not in data:
            print(f"  Note: slack_message field will be added by the script")
    except json.JSONDecodeError as e:
        print(f"[FAIL] PowerShell JSON scenario failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("Summary:")
    print("  - The fix: json.loads(json_str.encode().decode('utf-8-sig'))")
    print("  - Handles both normal JSON and UTF-8 BOM-prefixed JSON")
    print("  - Works correctly with PowerShell ConvertTo-Json output")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_json_parsing_with_bom()
    sys.exit(0 if success else 1)
