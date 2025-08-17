#!/usr/bin/env python3
"""
Test web interface accessibility for FitAgent
"""

import requests
import time
import subprocess
import json

def test_agent_web_interface():
    """Test if agent web interfaces are accessible"""
    
    print("🌐 Testing Agent Web Interfaces...")
    
    # Test different localhost variants
    test_urls = [
        "http://localhost:8081",
        "http://127.0.0.1:8081", 
        "http://0.0.0.0:8081",
        "http://localhost:8081/status",
        "http://127.0.0.1:8081/status",
        "http://localhost:8081/submit",
        "http://127.0.0.1:8081/submit"
    ]
    
    for url in test_urls:
        try:
            print(f"Testing: {url}")
            response = requests.get(url, timeout=3)
            print(f"  ✅ Status: {response.status_code}")
            if response.text:
                print(f"  📝 Content: {response.text[:100]}...")
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Connection refused")
        except requests.exceptions.Timeout:
            print(f"  ⏰ Timeout")
        except Exception as e:
            print(f"  ❌ Error: {e}")
        print()

def check_running_processes():
    """Check what's running on relevant ports"""
    
    print("🔍 Checking running processes...")
    
    ports = [8081, 8082, 8083]
    
    for port in ports:
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], 
                capture_output=True, 
                text=True
            )
            
            if result.stdout:
                print(f"Port {port}:")
                print(f"  {result.stdout.strip()}")
            else:
                print(f"Port {port}: Available")
        except Exception as e:
            print(f"Error checking port {port}: {e}")
        print()

def test_agentverse_inspector():
    """Test Agentverse inspector connectivity"""
    
    print("🔍 Testing Agentverse Inspector...")
    
    # Test basic Agentverse connectivity
    try:
        response = requests.get("https://agentverse.ai", timeout=10)
        print(f"✅ Agentverse.ai accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Agentverse.ai error: {e}")
    
    # Test inspector endpoint format
    test_agent_address = "agent1qgyy9tw86jglzejzvp7pxm52py5hufecxe7r8uazhhmphg95wvwtqnxz9xh"
    inspector_url = f"https://agentverse.ai/inspect/?uri=http%3A//127.0.0.1%3A8081&address={test_agent_address}"
    
    print(f"📍 Inspector URL format:")
    print(f"  {inspector_url}")
    
    try:
        response = requests.get(inspector_url, timeout=10)
        print(f"✅ Inspector page accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Inspector error: {e}")

if __name__ == "__main__":
    print("🧪 FitAgent Web Access Test\n")
    
    # Check running processes first
    check_running_processes()
    
    # Test web interfaces
    test_agent_web_interface()
    
    # Test Agentverse inspector
    test_agentverse_inspector()
    
    print("\n💡 Troubleshooting Tips:")
    print("1. uAgents typically don't serve web pages on their ports")
    print("2. The agent inspector is external (Agentverse.ai)")
    print("3. Agent communication happens via messages, not HTTP")
    print("4. Use the client script to test agent functionality")
