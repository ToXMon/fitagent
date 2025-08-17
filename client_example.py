"""
FitAgent Client Example - Demonstrates interaction with the FitAgent Nutrition Coach
"""

import asyncio
from datetime import datetime
from uuid import uuid4
from uagents import Agent, Context, Protocol

# Import FitAgent models
import sys
import os
sys.path.append(os.path.dirname(__file__))
from fitagent_coach import NutritionQuery, NutritionResponse, GoalUpdate, BehaviorInsight

# Initialize client agent
client_agent = Agent(
    name="fitagent_client",
    port=8083,
    mailbox=False,  # Disable for local testing
    seed="fitagent_client_seed"
)

# Create a simple protocol for FitAgent communication
fitagent_protocol = Protocol("FitAgentClientProtocol")

# FitAgent Coach address (update this with your actual agent address)
FITAGENT_COACH_ADDRESS = "agent1qgyy9tw86jglzejzvp7pxm52py5hufecxe7r8uazhhmphg95wvwtqnxz9xh"

@client_agent.on_event("startup")
async def startup_handler(ctx: Context):
    """Startup handler - demonstrates FitAgent interaction"""
    ctx.logger.info(f"FitAgent Client started: {ctx.agent.name} at {ctx.agent.address}")
    
    # Wait a moment for agent to be ready
    await asyncio.sleep(2)
    
    # Example 1: Basic nutrition query
    nutrition_query = NutritionQuery(
        user_id="demo_user_123",
        query="I just ate a grilled chicken breast with quinoa and steamed broccoli. How did I do nutritionally?",
        user_goals={
            "daily_protein": 120,
            "daily_calories": 2000,
            "goal_type": "muscle_gain"
        }
    )
    
    ctx.logger.info("Sending nutrition query to FitAgent Coach...")
    await ctx.send(FITAGENT_COACH_ADDRESS, nutrition_query)
    
    # Example 2: Goal update after a delay
    await asyncio.sleep(5)
    
    goal_update = GoalUpdate(
        user_id="demo_user_123",
        goal_type="daily_protein",
        current_value=85.0,
        target_value=120.0,
        timestamp=datetime.now()
    )
    
    ctx.logger.info("Sending goal update to FitAgent Coach...")
    await ctx.send(FITAGENT_COACH_ADDRESS, goal_update)

@fitagent_protocol.on_message(NutritionResponse)
async def handle_nutrition_response(ctx: Context, sender: str, msg: NutritionResponse):
    """Handle nutrition coaching responses"""
    ctx.logger.info(f"Received nutrition response from {sender}")
    ctx.logger.info(f"Analysis: {msg.analysis}")
    ctx.logger.info(f"Recommendations: {msg.recommendations}")
    ctx.logger.info(f"VP Tokens Earned: {msg.vp_tokens_earned}")
    ctx.logger.info(f"Next Steps: {msg.next_steps}")

@fitagent_protocol.on_message(BehaviorInsight)
async def handle_behavior_insight(ctx: Context, sender: str, msg: BehaviorInsight):
    """Handle behavior insights"""
    ctx.logger.info(f"Received behavior insight from {sender}")
    ctx.logger.info(f"Insight Type: {msg.insight_type}")
    ctx.logger.info(f"Confidence: {msg.confidence}")
    ctx.logger.info(f"Recommendations: {msg.recommendations}")

# Include the protocol
client_agent.include(fitagent_protocol, publish_manifest=True)

if __name__ == '__main__':
    print("🚀 Starting FitAgent Client Demo...")
    print(f"Will connect to FitAgent Coach at: {FITAGENT_COACH_ADDRESS}")
    print("This demo will:")
    print("1. Send a nutrition query about a healthy meal")
    print("2. Send a goal update for protein tracking")
    print("3. Display responses from the FitAgent Coach")
    print("\nStarting client...")
    
    client_agent.run()
