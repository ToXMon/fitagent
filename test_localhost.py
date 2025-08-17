#!/usr/bin/env python3
"""
Test localhost connectivity for FitAgent
"""

import os
import time
import asyncio
import requests
from dotenv import load_dotenv
from uagents import Agent, Context

load_dotenv()

def test_port_availability(port):
    """Test if port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0  # True if port is available

def find_available_port(start_port=8081):
    """Find next available port"""
    port = start_port
    while port < start_port + 10:
        if test_port_availability(port):
            return port
        port += 1
    return None

def test_agent_creation():
    """Test creating agent with different configurations"""
    
    print("🔍 Testing Agent Creation...")
    
    # Find available port
    available_port = find_available_port(8081)
    if not available_port:
        print("❌ No available ports found")
        return None
    
    print(f"✅ Using port: {available_port}")
    
    try:
        # Test basic agent creation
        test_agent = Agent(
            name="test_fitagent",
            port=available_port,
            seed="test_seed_123"
        )
        
        print(f"✅ Agent created successfully")
        print(f"📍 Agent address: {test_agent.address}")
        print(f"🌐 Agent endpoint: http://localhost:{available_port}")
        
        return test_agent, available_port
        
    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return None

def test_http_endpoint(port):
    """Test HTTP endpoint connectivity"""
    
    endpoints = [
        f"http://localhost:{port}",
        f"http://127.0.0.1:{port}",
        f"http://localhost:{port}/status",
        f"http://localhost:{port}/submit"
    ]
    
    print(f"\n🌐 Testing HTTP endpoints on port {port}...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint} - Connection refused")
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint} - Timeout")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

async def test_agent_startup(agent, port):
    """Test agent startup and basic functionality"""
    
    print(f"\n🚀 Testing agent startup...")
    
    @agent.on_event("startup")
    async def startup_handler(ctx: Context):
        print(f"✅ Agent started: {ctx.agent.address}")
        print(f"🌐 Listening on: http://localhost:{port}")
        
        # Stop agent after startup test
        await asyncio.sleep(2)
        ctx.logger.info("Test completed, stopping agent...")
        
    try:
        # Run agent for a short time
        await asyncio.wait_for(agent.run_async(), timeout=10)
        
    except asyncio.TimeoutError:
        print("✅ Agent startup test completed")
    except Exception as e:
        print(f"❌ Agent startup failed: {e}")

if __name__ == "__main__":
    print("🔧 FitAgent Localhost Connectivity Test\n")
    
    # Test agent creation
    result = test_agent_creation()
    if not result:
        exit(1)
    
    agent, port = result
    
    # Test HTTP endpoints
    test_http_endpoint(port)
    
    # Test agent startup
    print(f"\n🧪 Starting agent test (will auto-stop)...")
    try:
        asyncio.run(test_agent_startup(agent, port))
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    
    print(f"\n✅ Localhost connectivity test completed!")
    print(f"💡 Recommended port for FitAgent: {port}")
