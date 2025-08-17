"""
FitAgent Nutrition Coach - uAgent with Venice AI Integration
A specialized AI agent for personalized nutrition coaching and behavior change tracking.
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
from agent_metadata import AGENT_METADATA

# LangChain imports for Venice AI integration
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import LLMResult
from langchain_core.language_models.llms import LLM

import requests
import hashlib

# Load environment variables
load_dotenv()

# Venice AI LLM Implementation
class VeniceAILLM(LLM):
    """Custom LangChain LLM wrapper for Venice AI API"""
    
    api_key: str = Field(default_factory=lambda: os.getenv("VENICE_AI_API_KEY", ""))
    model: str = Field(default="llama-3.1-405b")
    base_url: str = Field(default="https://api.venice.ai/api/v1")
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=1000)
    
    @property
    def _llm_type(self) -> str:
        return "venice_ai"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Venice AI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            return f"Error calling Venice AI: {str(e)}"

# Data Models for FitAgent
class NutritionQuery(Model):
    """Model for nutrition-related queries"""
    user_id: str = Field(description="Unique user identifier")
    query: str = Field(description="User's nutrition question or food description")
    image_data: Optional[str] = Field(default=None, description="Base64 encoded food image")
    user_goals: Optional[Dict] = Field(default=None, description="User's nutrition goals")
    context: Optional[Dict] = Field(default=None, description="Additional context")

class NutritionResponse(Model):
    """Model for nutrition coaching responses"""
    analysis: str = Field(description="Detailed nutrition analysis")
    recommendations: List[str] = Field(description="Personalized recommendations")
    vp_tokens_earned: int = Field(description="VP tokens earned for this interaction")
    progress_update: Dict = Field(description="Progress tracking update")
    next_steps: List[str] = Field(description="Suggested next actions")

class GoalUpdate(Model):
    """Model for goal updates and progress tracking"""
    user_id: str = Field(description="User identifier")
    goal_type: str = Field(description="Type of goal (protein, calories, etc.)")
    current_value: float = Field(description="Current progress value")
    target_value: float = Field(description="Target goal value")
    timestamp: datetime = Field(description="Update timestamp")

class BehaviorInsight(Model):
    """Model for behavior change insights"""
    user_id: str = Field(description="User identifier")
    insight_type: str = Field(description="Type of behavioral insight")
    confidence: float = Field(description="Confidence score of the insight")
    recommendations: List[str] = Field(description="Behavior change recommendations")

# User Memory and Context Management
class UserMemoryManager:
    """Manages persistent user context and coaching history"""
    
    def __init__(self):
        self.user_data = {}
        self.data_file = "user_memory.json"
        self.load_user_data()
    
    def load_user_data(self):
        """Load user data from persistent storage"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.user_data = json.load(f)
        except Exception as e:
            print(f"Error loading user data: {e}")
            self.user_data = {}
    
    def save_user_data(self):
        """Save user data to persistent storage"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def get_user_context(self, user_id: str) -> Dict:
        """Get user's coaching context and history"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                "goals": {},
                "history": [],
                "preferences": {},
                "progress": {},
                "behavior_patterns": {},
                "created_at": datetime.now().isoformat(),
                "last_interaction": None
            }
        return self.user_data[user_id]
    
    def update_user_context(self, user_id: str, update_data: Dict):
        """Update user's context with new information"""
        context = self.get_user_context(user_id)
        context.update(update_data)
        context["last_interaction"] = datetime.now().isoformat()
        self.save_user_data()
    
    def add_interaction(self, user_id: str, query: str, response: str, analysis: Dict):
        """Add new interaction to user's history"""
        context = self.get_user_context(user_id)
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "analysis": analysis
        }
        context["history"].append(interaction)
        
        # Keep only last 50 interactions to manage memory
        if len(context["history"]) > 50:
            context["history"] = context["history"][-50:]
        
        self.save_user_data()

# Initialize Venice AI LLM and Memory Manager
venice_llm = VeniceAILLM()
memory_manager = UserMemoryManager()

# Create the FitAgent Coach
# Remove endpoint to enable proper mailbox functionality
fitagent_coach = Agent(
    name="fitagent_nutrition_coach",
    port=8081,
    seed="fitagent_coach_seed_phrase_for_consistency",
    mailbox=True,  # Mailbox mode for Agentverse visibility
    readme_path="README.md",
    publish_agent_details=True
)

# Nutrition Coaching Protocol
nutrition_protocol = Protocol("FitAgentNutritionCoaching")

def generate_coaching_prompt(user_context: Dict, query: str, image_data: Optional[str] = None) -> str:
    """Generate a comprehensive coaching prompt for Venice AI"""
    
    base_prompt = f"""
You are FitAgent, an expert nutrition coach and behavior change specialist. You provide personalized, 
evidence-based nutrition guidance that helps users achieve their health goals through sustainable habits.

USER CONTEXT:
- Goals: {user_context.get('goals', 'Not specified')}
- Preferences: {user_context.get('preferences', 'Not specified')}
- Progress: {user_context.get('progress', 'No progress data')}
- Recent History: {user_context.get('history', [])[-3:] if user_context.get('history') else 'No previous interactions'}

USER QUERY: {query}

{"IMAGE PROVIDED: Yes - analyze the food image for nutrition content" if image_data else "IMAGE PROVIDED: No"}

COACHING GUIDELINES:
1. Provide specific, actionable nutrition advice
2. Consider the user's goals and preferences
3. Suggest realistic behavior changes
4. Calculate approximate nutrition values if food is described/shown
5. Recommend VP token earning opportunities (healthy choices = more tokens)
6. Identify behavior patterns and suggest improvements
7. Keep responses encouraging and motivational

RESPONSE FORMAT:
Provide a JSON response with these fields:
- analysis: Detailed nutrition analysis
- recommendations: List of 3-5 specific recommendations
- vp_tokens_earned: Number (0-100 based on healthy choices)
- progress_update: Object with goal progress
- next_steps: List of 2-3 actionable next steps
- behavior_insights: Any patterns or insights about user behavior

Respond only with valid JSON.
"""
    
    return base_prompt

@nutrition_protocol.on_message(model=NutritionQuery, replies={NutritionResponse})
async def handle_nutrition_query(ctx: Context, sender: str, msg: NutritionQuery):
    """Handle nutrition coaching queries with Venice AI"""
    
    try:
        # Get user context from memory
        user_context = memory_manager.get_user_context(msg.user_id)
        
        # Generate coaching prompt
        prompt = generate_coaching_prompt(user_context, msg.query, msg.image_data)
        
        # Get response from Venice AI
        ctx.logger.info(f"Processing nutrition query for user {msg.user_id}")
        ai_response = venice_llm._call(prompt)
        
        # Parse AI response
        try:
            response_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # Fallback response if JSON parsing fails
            response_data = {
                "analysis": ai_response,
                "recommendations": ["Continue tracking your nutrition", "Stay hydrated", "Focus on whole foods"],
                "vp_tokens_earned": 10,
                "progress_update": {"status": "processing"},
                "next_steps": ["Log your next meal", "Check your goals"],
                "behavior_insights": "Keep up the great work!"
            }
        
        # Create response
        nutrition_response = NutritionResponse(
            analysis=response_data.get("analysis", "Analysis completed"),
            recommendations=response_data.get("recommendations", []),
            vp_tokens_earned=response_data.get("vp_tokens_earned", 10),
            progress_update=response_data.get("progress_update", {}),
            next_steps=response_data.get("next_steps", [])
        )
        
        # Update user memory
        memory_manager.add_interaction(
            msg.user_id, 
            msg.query, 
            nutrition_response.analysis,
            response_data
        )
        
        # Update user progress if goals are provided
        if msg.user_goals:
            memory_manager.update_user_context(msg.user_id, {"goals": msg.user_goals})
        
        ctx.logger.info(f"Sending nutrition response to {sender}")
        await ctx.send(sender, nutrition_response)
        
    except Exception as e:
        ctx.logger.error(f"Error processing nutrition query: {e}")
        
        # Send error response
        error_response = NutritionResponse(
            analysis=f"I apologize, but I encountered an error processing your request. Please try again.",
            recommendations=["Try rephrasing your question", "Check your internet connection"],
            vp_tokens_earned=5,
            progress_update={"error": str(e)},
            next_steps=["Retry your request", "Contact support if issue persists"]
        )
        await ctx.send(sender, error_response)

@nutrition_protocol.on_message(model=GoalUpdate, replies={BehaviorInsight})
async def handle_goal_update(ctx: Context, sender: str, msg: GoalUpdate):
    """Handle goal updates and provide behavior insights"""
    
    try:
        user_context = memory_manager.get_user_context(msg.user_id)
        
        # Update progress tracking
        if "progress" not in user_context:
            user_context["progress"] = {}
        
        user_context["progress"][msg.goal_type] = {
            "current": msg.current_value,
            "target": msg.target_value,
            "last_updated": msg.timestamp.isoformat(),
            "completion_rate": (msg.current_value / msg.target_value) * 100 if msg.target_value > 0 else 0
        }
        
        # Generate behavior insights
        insight_prompt = f"""
        Analyze this user's goal progress and provide behavior change insights:
        
        Goal Type: {msg.goal_type}
        Current Progress: {msg.current_value} / {msg.target_value}
        Completion Rate: {(msg.current_value / msg.target_value) * 100 if msg.target_value > 0 else 0}%
        
        User History: {user_context.get('history', [])[-5:]}
        
        Provide insights about behavior patterns and recommendations for improvement.
        Focus on sustainable habit formation and positive reinforcement.
        
        Respond with JSON containing:
        - insight_type: Type of insight (progress, habit, motivation, etc.)
        - confidence: Confidence score 0-1
        - recommendations: List of specific behavior change recommendations
        """
        
        ai_insight = venice_llm._call(insight_prompt)
        
        try:
            insight_data = json.loads(ai_insight)
        except json.JSONDecodeError:
            insight_data = {
                "insight_type": "progress",
                "confidence": 0.7,
                "recommendations": ["Continue tracking your progress", "Celebrate small wins", "Stay consistent"]
            }
        
        # Create behavior insight response
        behavior_insight = BehaviorInsight(
            user_id=msg.user_id,
            insight_type=insight_data.get("insight_type", "progress"),
            confidence=insight_data.get("confidence", 0.7),
            recommendations=insight_data.get("recommendations", [])
        )
        
        # Update user context
        memory_manager.update_user_context(msg.user_id, user_context)
        
        ctx.logger.info(f"Generated behavior insight for user {msg.user_id}")
        await ctx.send(sender, behavior_insight)
        
    except Exception as e:
        ctx.logger.error(f"Error processing goal update: {e}")

# Autonomous behavior - periodic user engagement
@fitagent_coach.on_interval(period=3600.0)  # Every hour
async def autonomous_user_engagement(ctx: Context):
    """Autonomous agent behavior - proactive user engagement"""
    
    try:
        # Check for users who haven't interacted recently
        current_time = datetime.now()
        
        for user_id, user_data in memory_manager.user_data.items():
            last_interaction = user_data.get("last_interaction")
            
            if last_interaction:
                last_time = datetime.fromisoformat(last_interaction)
                hours_since_last = (current_time - last_time).total_seconds() / 3600
                
                # Send proactive coaching for users inactive for 24+ hours
                if hours_since_last >= 24:
                    ctx.logger.info(f"Sending proactive coaching to inactive user {user_id}")
                    
                    # Generate proactive coaching message
                    proactive_prompt = f"""
                    Generate a motivational check-in message for a user who hasn't logged nutrition data in {hours_since_last:.1f} hours.
                    
                    User Goals: {user_data.get('goals', {})}
                    Recent Progress: {user_data.get('progress', {})}
                    
                    Create an encouraging message that:
                    1. Acknowledges their goals
                    2. Provides a gentle reminder
                    3. Offers specific, actionable advice
                    4. Mentions VP token earning opportunities
                    
                    Keep it positive and supportive, not pushy.
                    """
                    
                    proactive_message = venice_llm._call(proactive_prompt)
                    
                    # Log the proactive engagement
                    memory_manager.add_interaction(
                        user_id,
                        "Proactive coaching check-in",
                        proactive_message,
                        {"type": "proactive", "hours_inactive": hours_since_last}
                    )
        
    except Exception as e:
        ctx.logger.error(f"Error in autonomous engagement: {e}")

# Startup handler
@fitagent_coach.on_event("startup")
async def startup_handler(ctx: Context):
    """Agent startup handler with Agentverse registration"""
    ctx.logger.info(f"FitAgent Nutrition Coach started with address: {ctx.agent.address}")
    ctx.logger.info("Ready to provide personalized nutrition coaching!")
    
    # Print agent address prominently
    print(f"\n🤖 AGENT ADDRESS: {ctx.agent.address}")
    print(f"📍 Agent Inspector: https://agentverse.ai/inspect/?uri=http://localhost:8081&address={ctx.agent.address}")
    print(f"🔗 Use this address to communicate with the agent")
    
    # Print endpoint info - should be None for mailbox mode
    endpoint = os.environ.get("AGENT_ENDPOINT")
    if endpoint:
        print(f"🌐 Configured Endpoint: {endpoint}")
        print("⚠️  WARNING: Endpoint overrides mailbox functionality")
    else:
        print("🌐 Endpoint: None (mailbox mode enabled)")
    
    print(f"📋 Agent Metadata: {AGENT_METADATA['name']} - {AGENT_METADATA['description'][:100]}...")
    print(f"🏷️  Tags: {', '.join(AGENT_METADATA['tags'])}\n")
    
    # Initialize Venice AI connection
    try:
        test_response = venice_llm._call("Hello, this is a connection test.")
        ctx.logger.info("Venice AI connection successful")
        print("✅ Venice AI connection established")
    except Exception as e:
        ctx.logger.error(f"Venice AI connection failed: {e}")
        print(f"❌ Venice AI connection failed: {e}")
    
    # Log registration status
    api_key = os.environ.get("AGENTVERSE_API_KEY")
    if api_key:
        print("✅ AGENTVERSE_API_KEY found - Agent should register with Agentverse")
        ctx.logger.info("Agent configured for Agentverse registration")
    else:
        print("❌ AGENTVERSE_API_KEY missing - Agent will run locally only")
        ctx.logger.warning("No Agentverse API key found")

# Include the protocol
fitagent_coach.include(nutrition_protocol, publish_manifest=True)

# Register functions for Agentverse visibility
from uagents.query import query

# Define query models for Agentverse registration
class NutritionQueryRequest(Model):
    """Query model for nutrition coaching requests"""
    user_id: str = Field(description="User identifier")
    query: str = Field(description="Nutrition question or food description")
    user_goals: Optional[Dict] = Field(default=None, description="User's nutrition goals")

class NutritionQueryResponse(Model):
    """Response model for nutrition coaching"""
    analysis: str = Field(description="AI nutrition analysis")
    recommendations: List[str] = Field(description="Personalized recommendations")
    vp_tokens_earned: int = Field(description="VP tokens earned")
    success: bool = Field(description="Query success status")

@fitagent_coach.on_query(model=NutritionQueryRequest, replies={NutritionQueryResponse})
async def handle_nutrition_query_agentverse(ctx: Context, sender: str, msg: NutritionQueryRequest):
    """Handle nutrition queries from Agentverse - this makes the agent discoverable"""
    
    try:
        # Process query using existing logic
        result = await process_external_query(
            msg.user_id, 
            msg.query, 
            None,  # No image data from Agentverse queries
            msg.user_goals
        )
        
        # Return structured response
        response = NutritionQueryResponse(
            analysis=result.get("analysis", "Analysis completed"),
            recommendations=result.get("recommendations", []),
            vp_tokens_earned=result.get("vp_tokens_earned", 10),
            success=True
        )
        
        ctx.logger.info(f"Processed Agentverse query from {sender}")
        return response
        
    except Exception as e:
        ctx.logger.error(f"Error processing Agentverse query: {e}")
        
        # Return error response
        return NutritionQueryResponse(
            analysis=f"Error processing request: {str(e)}",
            recommendations=["Please try again", "Contact support if issue persists"],
            vp_tokens_earned=5,
            success=False
        )

# Direct API integration for external systems
async def process_external_query(user_id: str, query: str, image_data: Optional[str] = None, user_goals: Optional[Dict] = None) -> Dict:
    """Process external queries without LangChain adapter"""
    
    try:
        # Get user context
        user_context = memory_manager.get_user_context(user_id)
        
        # Generate coaching response
        prompt = generate_coaching_prompt(user_context, query, image_data)
        response = venice_llm._call(prompt)
        
        # Parse response
        try:
            response_data = json.loads(response)
        except json.JSONDecodeError:
            response_data = {
                "analysis": response,
                "recommendations": ["Continue tracking your nutrition", "Stay hydrated", "Focus on whole foods"],
                "vp_tokens_earned": 10,
                "progress_update": {"status": "processing"},
                "next_steps": ["Log your next meal", "Check your goals"],
                "behavior_insights": "Keep up the great work!"
            }
        
        # Update memory
        memory_manager.add_interaction(user_id, query, response, {"source": "external_api"})
        
        # Update user goals if provided
        if user_goals:
            memory_manager.update_user_context(user_id, {"goals": user_goals})
        
        return response_data
        
    except Exception as e:
        return {
            "analysis": f"Error processing request: {str(e)}",
            "recommendations": ["Try rephrasing your question", "Check your internet connection"],
            "vp_tokens_earned": 5,
            "progress_update": {"error": str(e)},
            "next_steps": ["Retry your request", "Contact support if issue persists"],
            "behavior_insights": "Please try again"
        }

# Main execution
if __name__ == "__main__":
    # Get API token for Agentverse registration
    API_TOKEN = os.environ.get("AGENTVERSE_API_KEY")
    
    if not API_TOKEN:
        print("Warning: AGENTVERSE_API_KEY not found. Agent will run locally only.")
        print("To register on Agentverse, set AGENTVERSE_API_KEY environment variable.")
    
    # Run the agent
    print("🚀 Starting FitAgent Nutrition Coach...")
    print(f"Agent Address: {fitagent_coach.address}")
    print("Ready to provide personalized nutrition coaching!")
    
    try:
        fitagent_coach.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down FitAgent Coach...")
        print("👋 FitAgent Coach stopped.")
