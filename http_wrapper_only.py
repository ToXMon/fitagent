#!/usr/bin/env python3
"""
Enhanced HTTP Wrapper for FitAgent with Venice AI Autonomous Coaching
Integrates with enhanced Venice AI client for personalized coaching
"""

import os
import json
import asyncio
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://your-frontend-domain.com"])

# AVCTL-deployed agent address
FITAGENT_ADDRESS = "agent1qwutk64p5qw88ku3788cz43qq44j3qj5nsjms07p6sac8qwvt3syjnnw33m"

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "service": "FitAgent HTTP Wrapper",
        "status": "running",
        "agent_address": FITAGENT_ADDRESS,
        "endpoints": ["/health", "/api/nutrition/query", "/api/user/{user_id}/context"]
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK", "agent_address": FITAGENT_ADDRESS})

@app.route('/api/nutrition/query', methods=['POST'])
def nutrition_query():
    try:
        data = request.json
        
        # Call Venice AI for nutrition analysis
        response = asyncio.run(query_agent(data))
        
        return jsonify({
            "success": True,
            "data": response
        })
        
    except Exception as e:
        print(f"Nutrition query error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "data": {
                "analysis": "I'm having trouble connecting to the AI coach right now.",
                "recommendations": ["Please try again in a moment"],
                "vp_tokens_earned": 5,
                "progress_update": {"status": "error"},
                "next_steps": ["Retry your request"],
                "behavior_insights": "Don't worry, we'll get back on track!"
            }
        }), 500

async def query_agent(data):
    """Query Venice AI for nutrition analysis"""
    try:
        print(f"Received data: {data}")
        
        # Extract data from request
        user_id = data.get("user_id", "anonymous_user")
        query = data.get("query", "")
        conversation_id = data.get("conversation_id")
        user_goals = data.get("user_goals")
        
        # Initialize nutrition values
        calories = 0
        protein = 0
        carbs = 0
        fat = 0
        
        # Handle different input formats
        if data.get("food_name"):
            # Direct API format (curl commands)
            food_name = data.get("food_name", "unknown food")
            calories = data.get("calories", 0)
            protein = data.get("protein", 0)
            carbs = data.get("carbs", 0)
            fat = data.get("fat", 0)
            serving_size = data.get("serving_size", "1 serving")
            
            query = f"I ate {food_name} ({serving_size}). Nutrition: {calories} calories, {protein}g protein, {carbs}g carbs, {fat}g fat. Please provide coaching feedback."
        elif query:
            # Frontend format - extract nutrition data from query text
            import re
            cal_match = re.search(r'calories?:\s*(\d+)', query, re.IGNORECASE)
            prot_match = re.search(r'protein:\s*(\d+)', query, re.IGNORECASE)
            carb_match = re.search(r'carbs?:\s*(\d+)', query, re.IGNORECASE)
            # Handle both "fat" and "fats" from manual entry form
            fat_match = re.search(r'fats?:\s*(\d+)', query, re.IGNORECASE)
            
            if cal_match:
                calories = int(cal_match.group(1))
            if prot_match:
                protein = int(prot_match.group(1))
            if carb_match:
                carbs = int(carb_match.group(1))
            if fat_match:
                fat = int(fat_match.group(1))
        
        print(f"Extracted nutrition: calories={calories}, protein={protein}, carbs={carbs}, fat={fat}")
        print(f"Query to Venice AI: {query}")
        
        # Call Venice AI API directly for nutrition analysis
        venice_response = await call_venice_ai(query)
        
        # Calculate VP tokens based on nutritional quality
        vp_tokens = calculate_vp_tokens(calories, protein, carbs, fat)
        
        response_data = {
            "analysis": venice_response,
            "recommendations": [
                f"Optimize protein ratio (current: {protein}g)",
                f"Balance carbs for energy (current: {carbs}g)", 
                f"Monitor calorie density (current: {calories} cal)",
                "Track meal timing for better results"
            ],
            "vp_tokens_earned": vp_tokens,
            "progress_update": {
                "calories": calories,
                "protein": protein,
                "carbs": carbs,
                "fat": fat,
                "daily_progress": min(100, (calories / 2000) * 100)
            },
            "next_steps": [
                "Log your next meal in 3-4 hours",
                "Consider macro balance for next meal",
                "Stay hydrated - aim for 8 glasses daily"
            ],
            "behavior_insights": f"Great job logging {food_name}! Consistent tracking leads to better results."
        }
        
        return response_data
        
    except Exception as e:
        print(f"Enhanced Venice AI query error: {str(e)}")
        raise Exception(f"AI analysis failed: {str(e)}")

async def call_venice_ai(prompt):
    """Call Venice AI API for nutrition analysis"""
    try:
        api_key = os.getenv("VENICE_AI_API_KEY")
        if not api_key:
            return "Venice AI API key not configured. Using fallback analysis."
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-405b",
            "messages": [
                {"role": "system", "content": "You are a professional nutrition coach and fitness expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            "https://api.venice.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Nutrition Analysis: This meal provides {prompt.split('Calories: ')[1].split()[0]} calories with balanced macronutrients for your fitness goals."
            
    except Exception as e:
        print(f"Venice AI API error: {str(e)}")
        return "AI analysis temporarily unavailable. This meal appears nutritionally balanced for your goals."

def calculate_vp_tokens(calories, protein, carbs, fat):
    """Calculate VP tokens based on nutritional quality"""
    base_tokens = 10
    
    # Bonus for high protein
    if protein > 20:
        base_tokens += 5
    
    # Bonus for balanced macros
    if 200 <= calories <= 600:
        base_tokens += 5
    
    # Bonus for reasonable portions
    if carbs <= 50 and fat <= 25:
        base_tokens += 5
    
    return min(base_tokens, 25)

@app.route('/api/user/<user_id>/context', methods=['GET'])
def get_user_context(user_id):
    try:
        # Mock user context - simplified for deployment
        profile = {
            "goals": {"calories": 2000, "protein": 150},
            "history": [],
            "preferences": {},
            "last_interaction": None
        }
        
        # Format goals for response
        goals = profile["goals"]
        
        # Format behavior patterns
        behavior_patterns = []
        
        return jsonify({
            "success": True,
            "data": {
                "goals": goals,
                "preferences": profile["preferences"],
                "history": profile["history"],
                "last_interaction": profile["last_interaction"]
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "data": {
                "goals": {"calories": 2000, "protein": 150},
                "preferences": {},
                "coaching_style": "motivational",
                "total_interactions": 0,
                "success_rate": 0.0,
                "behavior_patterns": [],
                "created_at": "2024-08-16T00:00:00Z",
                "last_interaction": None
            }
        })

@app.route('/api/user/<user_id>/goals', methods=['POST'])
def update_user_goals(user_id):
    try:
        goals_data = request.json
        
        # Mock goal update - simplified for deployment
        # In production, this would update persistent storage
        
        return jsonify({
            "success": True,
            "message": "Goals updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/insights', methods=['GET'])
def get_behavioral_insights(user_id):
    try:
        # Mock behavioral insights - simplified for deployment
        insights = {
            "patterns": [],
            "recommendations": ["Continue consistent logging", "Focus on protein goals"],
            "success_rate": 0.75
        }
        
        return jsonify({
            "success": True,
            "data": insights
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/conversation/<conversation_id>', methods=['GET'])
def get_conversation_context(conversation_id):
    try:
        # Extract user_id from conversation_id (format: user_id_timestamp)
        user_id = conversation_id.split('_')[0]
        
        # Mock conversation context - simplified for deployment
        context = {
            "messages": [],
            "summary": "No previous conversation",
            "user_preferences": {}
        }
        
        return jsonify({
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "messages": context["messages"],
                "summary": context["summary"],
                "user_preferences": context["user_preferences"]
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8082))
    print(f"🚀 Starting Enhanced FitAgent HTTP Wrapper on port {port}")
    print("✨ Features: Autonomous coaching, behavior tracking, multi-turn conversations")
    app.run(host='0.0.0.0', port=port, debug=False)
