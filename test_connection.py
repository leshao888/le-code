"""Test script to verify API connection and basic functionality."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.settings import settings
from config.models import ModelRegistry

# Check API Key
api_key = settings.API_KEY
if not api_key:
    print("[ERROR] API_KEY not found. Please set it in config.json or via AI_API_KEY environment variable")
    sys.exit(1)

print(f"[OK] API Key found: {api_key[:20]}...{api_key[-4:]}")

# Check model configuration
model_name = settings.MODEL
model_config = ModelRegistry.get_model_config(model_name)
if not model_config:
    print(f"[ERROR] Model '{model_name}' not found.")
    print(f"[INFO] Available models: {', '.join(ModelRegistry.list_all_models())}")
    sys.exit(1)

print(f"[OK] Model: {model_name}")
print(f"[OK] Provider: {model_config.get('provider', 'unknown')}")
print(f"[OK] Base URL: {model_config.get('base_url', '')}")

# Test API connection
print("\n[INFO] Testing API connection...")

try:
    from ai.client import AIClient

    client = AIClient()

    # Health check
    if client.health_check():
        print("[OK] API Connection Successful!")
    else:
        print("[ERROR] API health check failed")
        sys.exit(1)

    # Test with a simple message
    print("[INFO] Sending test request...")

    response = client.create_message(
        messages=[{"role": "user", "content": "请用一句话回复：你好"}],
        stream=False
    )

    # Display response
    if response.get("content"):
        print(f"\n[OK] API Connection Successful!")
        print(f"[AI] Response: {response['content']}")
        print(f"[USAGE] {response.get('usage', {}).get('input_tokens', 0)} input tokens, {response.get('usage', {}).get('output_tokens', 0)} output tokens")
    else:
        print("[WARNING] API connected but no response content")

    print("\n[SUCCESS] All tests passed! The program is ready to use.")
    print("\n[INFO] To start the interactive program, run:")
    print("   python main.py")
    print("\n   Or double-click run.bat")

except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
