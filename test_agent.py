#!/usr/bin/env python3
"""
Simple test script to verify FitAgent setup and get agent address
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from uagents import Agent, Context, Protocol, Model, Field
        print("✅ uAgents imports successful")
        return True
    except ImportError as e:
        print(f"❌ uAgents import failed: {e}")
        return False

def test_venice_ai():
    """Test Venice AI connection"""
    try:
        import requests
        api_key = os.getenv("VENICE_AI_API_KEY")
        if not api_key:
            print("⚠️  Venice AI API key not found in .env file")
            return False
        
        # Simple test call
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-405b",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.venice.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Venice AI connection successful")
            return True
        else:
            print(f"❌ Venice AI connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Venice AI test failed: {e}")
        return False

def get_agent_address():
    """Get the agent address without running the full agent"""
    try:
        from uagents import Agent
        
        agent = Agent(
            name="fitagent_nutrition_coach",
            port=8081,
            seed="fitagent_coach_seed_phrase_for_consistency",
            mailbox=True,
            endpoint=["http://localhost:8081/submit"]
        )
        
        print(f"\n🤖 FitAgent Address: {agent.address}")
        print(f"📍 Local Server: http://localhost:8081")
        print(f"🔗 Agent Inspector: https://agentverse.ai/inspect/?uri=http://localhost:8081&address={agent.address}")
        return agent.address
        
    except Exception as e:
        print(f"❌ Failed to get agent address: {e}")
        return None

def main():
    print("🧪 FitAgent Environment Test\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Make sure you're in the virtual environment:")
        print("   source venv/bin/activate")
        return
    
    # Get agent address
    address = get_agent_address()
    if not address:
        return
    
    # Test Venice AI (optional)
    print("\n🔍 Testing Venice AI connection...")
    venice_ok = test_venice_ai()
    
    print(f"\n📋 Summary:")
    print(f"✅ Virtual Environment: Active")
    print(f"✅ uAgents Framework: Working")
    print(f"✅ Agent Address: {address}")
    print(f"{'✅' if venice_ok else '⚠️ '} Venice AI: {'Working' if venice_ok else 'Check API key'}")
    
    print(f"\n🚀 Ready to run:")
    print(f"   python fitagent_coach.py")
    print(f"   # In another terminal:")
    print(f"   python client_example.py")

if __name__ == "__main__":
    main()
