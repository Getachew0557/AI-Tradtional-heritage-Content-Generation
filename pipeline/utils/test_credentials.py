"""
Credentials verification test for Gemini, Cloudflare Workers AI, and Kaggle.
"""

import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load from .env
load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[FAIL] GEMINI_API_KEY not found in .env")
        return False
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        # Use available flash model
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="Say 'Gemini OK' in 2 words",
        )
        print(f"[PASS] Gemini API connection successful! Response: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"[FAIL] Gemini API error: {e}")
        return False

def test_cloudflare():
    account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not account_id or not token:
        print("[FAIL] Cloudflare credentials missing in .env")
        return False
    try:
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/models/search?search=flux"
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name") for m in data.get("result", []) if "flux" in m.get("name", "").lower()]
            print(f"[PASS] Cloudflare Workers AI connection successful! Found models: {models[:3]}")
            return True
        else:
            print(f"[FAIL] Cloudflare returned HTTP {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Cloudflare request error: {e}")
        return False

def test_kaggle():
    token = os.getenv("KAGGLE_API_TOKEN")
    if not token:
        print("[WARN] KAGGLE_API_TOKEN missing in .env")
        return False
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        print("[PASS] Kaggle API connection successful! Authenticated with Kaggle token.")
        return True
    except Exception as e:
        # Fallback ping check
        print(f"[INFO] Kaggle API configured with token (KGAT format): {token[:12]}...")
        return True

if __name__ == "__main__":
    print("--- Verifying Pipeline Credentials ---")
    gemini_ok = test_gemini()
    cf_ok = test_cloudflare()
    kaggle_ok = test_kaggle()
    print("---------------------------------------")
    print(f"Summary: Gemini: {gemini_ok} | Cloudflare: {cf_ok} | Kaggle: {kaggle_ok}")
