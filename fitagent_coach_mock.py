"""
FitAgent Nutrition Coach - Mock Version (No Venice AI Required)
For testing without Venice AI API key
"""

import os
import time
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# uAgents framework imports
from uagents import Agent, Context, Protocol, Model
from uagents import Field

# Load environment variables
load_dotenv()

# Mock Venice AI LLM Implementation
class MockVeniceAILLM:
    """Mock LLM for testing without Venice AI API"""
    
    def _call(self, prompt: str) -> str:
        """Mock response based on prompt content"""
        
        if "nutrition" in prompt.lower() or "food" in prompt.lower():
            return json.dumps({
                "analysis": "Great choice! This meal provides excellent protein and nutrients.",
                "recommendations": [
                    "Continue with lean proteins like chicken",
                    "Add more colorful vegetables for vitamins",
                    "Stay hydrated throughout the day"
                ],
                "vp_tokens_earned": 25,
                "progress_update": {"protein_progress": "Good", "daily_goal": "On track"},
                "next_steps": ["Log your next meal", "Take a progress photo"],
                "behavior_insights": "You're building healthy eating habits!"
            })
        
        elif "goal" in prompt.lower() or "progress" in prompt.lower():
            return json.dumps({
                "insight_type": "progress",
                "confidence": 0.8,
                "recommendations": [
                    "You're making steady progress toward your goals",
                    "Consider increasing protein intake by 10g",
                    "Celebrate your consistency!"
                ]
            })
        
        else:
            return json.dumps({
                "analysis": "Thank you for your question! I'm here to help with nutrition coaching.",
                "recommendations": ["Ask me about your meals", "Set nutrition goals", "Track your progress"],
                "vp_tokens_earned": 5,
                "progress_update": {"status": "ready"},
                "next_steps": ["Share your next meal", "Set daily goals"]
            })

# Data Models (same as original)
class NutritionQuery(Model):
    user_id: str = Field(description="Unique user identifier")
    query: str = Field(description="User's nutrition question or food description")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded food image")
    user_goals: Optional[Dict] = Field(default=None, description="User's nutrition goals")
    context: Optional[Dict] = Field(default=None, description="Additional context")

class NutritionResponse(Model):
    analysis: str = Field(description="Detailed nutrition analysis")
    recommendations: List[str] = Field(description="Personalized recommendations")
    vp_tokens_earned: int = Field(description="VP tokens earned for this interaction")
    progress_update: Dict = Field(description="Progress tracking update")
    next_steps: List[str] = Field(description="Suggested next actions")

class GoalUpdate(Model):
    user_id: str = Field(description="User identifier")
    goal_type: str = Field(description="Type of goal (protein, calories, etc.)")
    current_value: float = Field(description="Current progress value")
    target_value: float = Field(description="Target goal value")
    timestamp: datetime = Field(description="Update timestamp")

class BehaviorInsight(Model):
    user_id: str = Field(description="User identifier")
    insight_type: str = Field(description="Type of behavioral insight")
    confidence: float = Field(description="Confidence score of the insight")
    recommendations: List[str] = Field(description="Behavior change recommendations")

# Simple memory manager
class SimpleMemoryManager:
    def __init__(self):
        self.user_data = {}
    
    def get_user_context(self, user_id: str) -> Dict:
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "goals": {},
                "history": [],
                "preferences": {},
                "progress": {},
                "created_at": datetime.now().isoformat()
            }
        return self.user_data[user_id]
    
    def update_user_context(self, user_id: str, update_data: Dict):
        context = self.get_user_context(user_id)
        context.update(update_data)
    
    def add_interaction(self, user_id: str, query: str, response: str, analysis: Dict):
        context = self.get_user_context(user_id)
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "analysis": analysis
        }
        context["history"].append(interaction)

# Initialize components
mock_llm = MockVeniceAILLM()
memory_manager = SimpleMemoryManager()

# Create the FitAgent Coach
fitagent_coach = Agent(
    name="fitagent_nutrition_coach_mock",
    port=8083,
    seed="fitagent_mock_coach_seed",
    mailbox=True,
    endpoint=["http://localhost:8083/submit"]
)

# Nutrition Coaching Protocol
nutrition_protocol = Protocol("FitAgentNutritionCoaching")

@nutrition_protocol.on_message(model=NutritionQuery, replies={NutritionResponse})
async def handle_nutrition_query(ctx: Context, sender: str, msg: NutritionQuery):
    """Handle nutrition coaching queries with mock AI"""
    
    try:
        # Get user context
        user_context = memory_manager.get_user_context(msg.user_id)
        
        # Generate mock prompt
        prompt = f"User query: {msg.query}. Goals: {msg.user_goals}"
        
        # Get mock response
        ctx.logger.info(f"Processing nutrition query for user {msg.user_id}")
        ai_response = mock_llm._call(prompt)
        
        # Parse response
        try:
            response_data = json.loads(ai_response)
        except json.JSONDecodeError:
            response_data = {
                "analysis": "Mock analysis completed",
                "recommendations": ["Stay healthy", "Keep tracking"],
                "vp_tokens_earned": 10,
                "progress_update": {"status": "mock_mode"},
                "next_steps": ["Continue logging meals"]
            }
        
        # Create response
        nutrition_response = NutritionResponse(
            analysis=response_data.get("analysis", "Mock analysis"),
            recommendations=response_data.get("recommendations", []),
            vp_tokens_earned=response_data.get("vp_tokens_earned", 10),
            progress_update=response_data.get("progress_update", {}),
            next_steps=response_data.get("next_steps", [])
        )
        
        # Update memory
        memory_manager.add_interaction(
            msg.user_id, 
            msg.query, 
            nutrition_response.analysis,
            response_data
        )
        
        ctx.logger.info(f"Sending mock nutrition response to {sender}")
        await ctx.send(sender, nutrition_response)
        
    except Exception as e:
        ctx.logger.error(f"Error processing nutrition query: {e}")

@nutrition_protocol.on_message(model=GoalUpdate, replies={BehaviorInsight})
async def handle_goal_update(ctx: Context, sender: str, msg: GoalUpdate):
    """Handle goal updates with mock insights"""
    
    try:
        user_context = memory_manager.get_user_context(msg.user_id)
        
        # Mock insight generation
        insight_data = {
            "insight_type": "progress",
            "confidence": 0.8,
            "recommendations": [
                f"Great progress on {msg.goal_type}!",
                f"You're at {msg.current_value}/{msg.target_value}",
                "Keep up the excellent work!"
            ]
        }
        
        behavior_insight = BehaviorInsight(
            user_id=msg.user_id,
            insight_type=insight_data["insight_type"],
            confidence=insight_data["confidence"],
            recommendations=insight_data["recommendations"]
        )
        
        ctx.logger.info(f"Generated mock behavior insight for user {msg.user_id}")
        await ctx.send(sender, behavior_insight)
        
    except Exception as e:
        ctx.logger.error(f"Error processing goal update: {e}")

@fitagent_coach.on_event("startup")
async def startup_handler(ctx: Context):
    """Agent startup handler"""
    ctx.logger.info(f"FitAgent Mock Coach started with address: {ctx.agent.address}")
    
    print(f"\n🤖 MOCK AGENT ADDRESS: {ctx.agent.address}")
    print(f"📍 Mock Agent Inspector: https://agentverse.ai/inspect/?uri=http://localhost:8083&address={ctx.agent.address}")
    print(f"🔗 Use this address to test agent communication\n")
    print("🧪 MOCK MODE: No Venice AI required - using mock responses")

# Include the protocol
fitagent_coach.include(nutrition_protocol, publish_manifest=True)

if __name__ == "__main__":
    print("🧪 Starting FitAgent Mock Coach (No Venice AI Required)...")
    print(f"Mock Agent Address: {fitagent_coach.address}")
    print("Ready for testing!")
    
    try:
        fitagent_coach.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Mock FitAgent Coach...")
        print("👋 Mock Agent stopped.")
