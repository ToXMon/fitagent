"""
Agent metadata for Agentverse registration
This file defines the agent's public information and capabilities
"""

AGENT_METADATA = {
    "name": "FitAgent Nutrition Coach",
    "description": "AI-powered nutrition coach providing personalized dietary guidance and behavior change support using Venice AI. Helps users track nutrition, earn VP tokens, and achieve health goals through evidence-based coaching.",
    "version": "1.0.0",
    "author": "FitAgent Team",
    "tags": ["nutrition", "health", "AI", "coaching", "venice-ai", "hackathon"],
    "capabilities": [
        "Personalized nutrition analysis",
        "Meal photo analysis", 
        "Dietary recommendations",
        "Progress tracking",
        "VP token rewards",
        "Behavior change coaching"
    ],
    "use_cases": [
        "Analyze meal nutrition content",
        "Get personalized dietary advice",
        "Track nutrition goals and progress",
        "Receive behavior change coaching",
        "Earn VP tokens for healthy choices"
    ],
    "models": {
        "query": "NutritionQueryRequest",
        "response": "NutritionQueryResponse"
    },
    "endpoints": {
        "nutrition_query": {
            "description": "Get AI nutrition coaching and analysis",
            "input": "User ID, nutrition query, and optional goals",
            "output": "Detailed analysis, recommendations, and VP tokens"
        }
    },
    "external_integrations": [
        "Venice AI LLM",
        "Akash Network deployment",
        "Base blockchain (VP tokens)",
        "Flow blockchain (NFT evolution)"
    ]
}
