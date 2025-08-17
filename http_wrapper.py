"""
HTTP REST API wrapper for FitAgent uAgent
Provides REST endpoints for frontend integration while maintaining uAgent functionality
"""

import os
import json
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
from fitagent_coach import process_external_query, memory_manager

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

@app.route('/', methods=['GET'])
def root():
    """Root endpoint - shows service info"""
    return jsonify({
        "service": "FitAgent Nutrition Coach API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/nutrition/query": "POST - Process nutrition queries",
            "/api/user/<user_id>/context": "GET - Get user context",
            "/api/user/<user_id>/goals": "POST - Update user goals",
            "/api/user/<user_id>/history": "GET - Get user history"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "OK", "service": "FitAgent Nutrition Coach"})

@app.route('/api/nutrition/query', methods=['POST'])
def nutrition_query():
    """Process nutrition queries from frontend"""
    try:
        data = request.get_json()
        
        # Extract required fields
        user_id = data.get('user_id', 'anonymous')
        query = data.get('query', '')
        image_data = data.get('image_data')
        user_goals = data.get('user_goals')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Process query using the agent's logic
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            process_external_query(user_id, query, image_data, user_goals)
        )
        
        loop.close()
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/context', methods=['GET'])
def get_user_context(user_id):
    """Get user's coaching context and history"""
    try:
        context = memory_manager.get_user_context(user_id)
        return jsonify({
            "success": True,
            "data": context
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/goals', methods=['POST'])
def update_user_goals(user_id):
    """Update user's nutrition goals"""
    try:
        goals = request.get_json()
        memory_manager.update_user_context(user_id, {"goals": goals})
        
        return jsonify({
            "success": True,
            "message": "Goals updated successfully"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/user/<user_id>/history', methods=['GET'])
def get_user_history(user_id):
    """Get user's interaction history"""
    try:
        context = memory_manager.get_user_context(user_id)
        history = context.get('history', [])
        
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Run Flask app
    app.run(host='0.0.0.0', port=8082, debug=False)
