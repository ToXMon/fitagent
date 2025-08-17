#!/usr/bin/env python3
"""
Debug Venice AI API connection with detailed error reporting
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_venice_api_detailed():
    """Test Venice AI with detailed debugging"""
    
    api_key = os.getenv("VENICE_AI_API_KEY")
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else api_key}")
    
    # Test different authentication methods
    auth_methods = [
        {"Authorization": f"Bearer {api_key}"},
        {"Authorization": f"API-Key {api_key}"},
        {"X-API-Key": api_key},
        {"api-key": api_key}
    ]
    
    endpoints = [
        "https://api.venice.ai/api/v1/chat/completions",
        "https://api.venice.ai/v1/chat/completions",
        "https://venice.ai/api/v1/chat/completions"
    ]
    
    payload = {
        "model": "llama-3.1-405b",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    for i, endpoint in enumerate(endpoints):
        print(f"\n🌐 Testing endpoint {i+1}: {endpoint}")
        
        for j, headers in enumerate(auth_methods):
            print(f"   🔐 Auth method {j+1}: {list(headers.keys())[0]}")
            
            try:
                response = requests.post(
                    endpoint,
                    headers={**headers, "Content-Type": "application/json"},
                    json=payload,
                    timeout=10
                )
                
                print(f"   📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ SUCCESS!")
                    try:
                        data = response.json()
                        print(f"   📝 Response: {data}")
                        return True
                    except:
                        print(f"   📝 Raw response: {response.text[:200]}")
                        return True
                        
                elif response.status_code == 401:
                    print(f"   ❌ 401 Unauthorized")
                    try:
                        error_data = response.json()
                        print(f"   📝 Error details: {error_data}")
                    except:
                        print(f"   📝 Raw error: {response.text[:200]}")
                        
                elif response.status_code == 404:
                    print(f"   ❌ 404 Not Found - Wrong endpoint")
                    
                else:
                    print(f"   ❌ Error {response.status_code}")
                    print(f"   📝 Response: {response.text[:200]}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
    
    return False

def test_alternative_models():
    """Test with different model names"""
    
    api_key = os.getenv("VENICE_AI_API_KEY")
    endpoint = "https://api.venice.ai/api/v1/chat/completions"
    
    models = [
        "llama-3.1-405b",
        "llama-3.1-70b", 
        "llama-3.1-8b",
        "gpt-4",
        "claude-3-sonnet"
    ]
    
    print(f"\n🤖 Testing different models...")
    
    for model in models:
        print(f"   Testing {model}...")
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"   ✅ {model} works!")
                return model
            else:
                print(f"   ❌ {model} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {model} error: {e}")
    
    return None

if __name__ == "__main__":
    print("🔍 Venice AI Debug Test\n")
    
    # Test API connection
    success = test_venice_api_detailed()
    
    if not success:
        print("\n🔄 Trying alternative models...")
        working_model = test_alternative_models()
        
        if working_model:
            print(f"\n✅ Found working model: {working_model}")
        else:
            print(f"\n❌ No working configuration found")
            print(f"\n💡 Suggestions:")
            print(f"   1. Verify API key is correct on Venice AI dashboard")
            print(f"   2. Check if API key has proper permissions")
            print(f"   3. Verify account has credits/usage remaining")
            print(f"   4. Try regenerating the API key")
    else:
        print(f"\n✅ Venice AI connection working!")
