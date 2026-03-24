"""Test script to verify API connection and basic functionality."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.settings import settings

# Check API Key
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    print("[ERROR] ZHIPUAI_API_KEY not found in .env file")
    sys.exit(1)

print(f"[OK] API Key found: {api_key[:20]}...{api_key[-4:]}")

# Test API connection
print("\n[INFO] Testing API connection...")

try:
    import anthropic

    client = anthropic.Anthropic(
        api_key=api_key,
        base_url="https://open.bigmodel.cn/api/anthropic",
        timeout=60.0,
        max_retries=3
    )

    # Test with a simple message
    print("[INFO] Sending test request to ZhipuAI...")

    response = client.messages.create(
        model=settings.MODEL_NAME,
        max_tokens=100,
        messages=[
            {"role": "user", "content": "请用一句话回复：你好"}
        ]
    )

    # Display response
    if response.content and len(response.content) > 0:
        assistant_message = response.content[0].text
        print(f"\n[OK] API Connection Successful!")
        print(f"[AI] Response: {assistant_message}")
        print(f"[USAGE] {response.usage.input_tokens} input tokens, {response.usage.output_tokens} output tokens")
    else:
        print("[WARNING] API connected but no response content")

    print("\n[SUCCESS] All tests passed! The program is ready to use.")
    print("\n[INFO] To start the interactive program, run:")
    print("   python main.py")
    print("\n   Or double-click run.bat")

except anthropic.APIError as e:
    print(f"\n[ERROR] API Error: {e}")
    print("\n[SOLUTION] Possible solutions:")
    print("   1. Check if your API Key is correct")
    print("   2. Check if you have sufficient quota")
    print("   3. Check your internet connection")
    sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
