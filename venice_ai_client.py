"""
Enhanced Venice AI Client with Autonomous Coaching and Memory
Implements sophisticated user context management, goal adjustment, and behavioral tracking
"""

import os
import json
import asyncio
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from collections import defaultdict
import requests
from dotenv import load_dotenv

load_dotenv()

class CoachingStyle(Enum):
    """Different coaching approaches based on user behavior patterns"""
    MOTIVATIONAL = "motivational"
    ANALYTICAL = "analytical"
    SUPPORTIVE = "supportive"
    CHALLENGING = "challenging"
    EDUCATIONAL = "educational"

class GoalStatus(Enum):
    """Goal achievement status"""
    ON_TRACK = "on_track"
    BEHIND = "behind"
    AHEAD = "ahead"
    STAGNANT = "stagnant"
    IMPROVING = "improving"

@dataclass
class UserGoal:
    """Enhanced user goal with progress tracking"""
    goal_type: str
    target_value: float
    current_value: float
    deadline: Optional[datetime]
    priority: int  # 1-5, 5 being highest
    created_at: datetime
    last_updated: datetime
    status: GoalStatus
    adjustment_history: List[Dict]
    
    @property
    def completion_rate(self) -> float:
        """Calculate goal completion percentage"""
        if self.target_value == 0:
            return 0.0
        return min(100.0, (self.current_value / self.target_value) * 100)
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Days until goal deadline"""
        if not self.deadline:
            return None
        return (self.deadline - datetime.now()).days

@dataclass
class BehaviorPattern:
    """User behavior pattern analysis"""
    pattern_type: str
    confidence: float
    frequency: int
    last_occurrence: datetime
    triggers: List[str]
    recommendations: List[str]

@dataclass
class ConversationContext:
    """Multi-turn conversation context"""
    conversation_id: str
    messages: List[Dict]
    topic: str
    sentiment: str
    coaching_style: CoachingStyle
    created_at: datetime
    last_active: datetime

class EnhancedVeniceAIClient:
    """Enhanced Venice AI client with autonomous coaching and memory"""
    
    def __init__(self, db_path: str = "fitagent_memory.db"):
        self.api_key = os.getenv("VENICE_AI_API_KEY")
        self.base_url = "https://api.venice.ai/api/v1"
        self.db_path = db_path
        self.init_database()
        
        # Coaching parameters
        self.coaching_styles = {
            CoachingStyle.MOTIVATIONAL: "encouraging, energetic, focus on achievements",
            CoachingStyle.ANALYTICAL: "data-driven, detailed, focus on metrics",
            CoachingStyle.SUPPORTIVE: "empathetic, understanding, focus on emotional support",
            CoachingStyle.CHALLENGING: "direct, goal-oriented, focus on pushing limits",
            CoachingStyle.EDUCATIONAL: "informative, explanatory, focus on learning"
        }
    
    def init_database(self):
        """Initialize SQLite database for persistent memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                coaching_style TEXT,
                preferences TEXT,
                created_at TIMESTAMP,
                last_interaction TIMESTAMP,
                total_interactions INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0
            )
        ''')
        
        # Goals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                goal_type TEXT,
                target_value REAL,
                current_value REAL,
                deadline TIMESTAMP,
                priority INTEGER,
                status TEXT,
                created_at TIMESTAMP,
                last_updated TIMESTAMP,
                adjustment_history TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                conversation_id TEXT,
                query TEXT,
                response TEXT,
                sentiment REAL,
                vp_tokens_earned INTEGER,
                timestamp TIMESTAMP,
                context TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Behavior patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS behavior_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                pattern_type TEXT,
                confidence REAL,
                frequency INTEGER,
                last_occurrence TIMESTAMP,
                triggers TEXT,
                recommendations TEXT,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT,
                topic TEXT,
                coaching_style TEXT,
                sentiment TEXT,
                messages TEXT,
                created_at TIMESTAMP,
                last_active TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def call_venice_ai(self, prompt: str, system_message: str = None, temperature: float = 0.7) -> str:
        """Enhanced Venice AI API call with error handling"""
        if not self.api_key:
            return "Venice AI API key not configured. Using fallback analysis."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "llama-3.1-405b",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
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
            print(f"Venice AI API error: {str(e)}")
            return f"AI analysis temporarily unavailable: {str(e)}"
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get comprehensive user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get basic profile
        cursor.execute('''
            SELECT coaching_style, preferences, created_at, last_interaction, 
                   total_interactions, success_rate
            FROM user_profiles WHERE user_id = ?
        ''', (user_id,))
        
        profile = cursor.fetchone()
        if not profile:
            # Create new user profile
            self.create_user_profile(user_id)
            profile = (CoachingStyle.MOTIVATIONAL.value, "{}", datetime.now(), None, 0, 0.0)
        
        # Get goals
        cursor.execute('''
            SELECT goal_type, target_value, current_value, deadline, priority, 
                   status, created_at, last_updated, adjustment_history
            FROM user_goals WHERE user_id = ?
        ''', (user_id,))
        
        goals_data = cursor.fetchall()
        goals = []
        for goal_data in goals_data:
            goals.append(UserGoal(
                goal_type=goal_data[0],
                target_value=goal_data[1],
                current_value=goal_data[2],
                deadline=datetime.fromisoformat(goal_data[3]) if goal_data[3] else None,
                priority=goal_data[4],
                status=GoalStatus(goal_data[5]),
                created_at=datetime.fromisoformat(goal_data[6]),
                last_updated=datetime.fromisoformat(goal_data[7]),
                adjustment_history=json.loads(goal_data[8]) if goal_data[8] else []
            ))
        
        # Get behavior patterns
        cursor.execute('''
            SELECT pattern_type, confidence, frequency, last_occurrence, triggers, recommendations
            FROM behavior_patterns WHERE user_id = ?
        ''', (user_id,))
        
        patterns_data = cursor.fetchall()
        patterns = []
        for pattern_data in patterns_data:
            patterns.append(BehaviorPattern(
                pattern_type=pattern_data[0],
                confidence=pattern_data[1],
                frequency=pattern_data[2],
                last_occurrence=datetime.fromisoformat(pattern_data[3]),
                triggers=json.loads(pattern_data[4]) if pattern_data[4] else [],
                recommendations=json.loads(pattern_data[5]) if pattern_data[5] else []
            ))
        
        conn.close()
        
        return {
            "user_id": user_id,
            "coaching_style": CoachingStyle(profile[0]),
            "preferences": json.loads(profile[1]) if profile[1] else {},
            "created_at": profile[2],
            "last_interaction": profile[3],
            "total_interactions": profile[4],
            "success_rate": profile[5],
            "goals": goals,
            "behavior_patterns": patterns
        }
    
    def create_user_profile(self, user_id: str):
        """Create new user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_profiles 
            (user_id, coaching_style, preferences, created_at, total_interactions, success_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, CoachingStyle.MOTIVATIONAL.value, "{}", datetime.now(), 0, 0.0))
        
        conn.commit()
        conn.close()
    
    async def autonomous_goal_adjustment(self, user_id: str) -> Dict:
        """Autonomously adjust user goals based on progress patterns"""
        profile = self.get_user_profile(user_id)
        adjustments = []
        
        for goal in profile["goals"]:
            # Analyze goal progress
            days_since_update = (datetime.now() - goal.last_updated).days
            
            # Auto-adjust based on patterns
            if goal.status == GoalStatus.AHEAD and goal.completion_rate > 120:
                # User is exceeding goals - increase target
                new_target = goal.target_value * 1.2
                adjustment = {
                    "goal_type": goal.goal_type,
                    "old_target": goal.target_value,
                    "new_target": new_target,
                    "reason": "Consistently exceeding target",
                    "timestamp": datetime.now().isoformat()
                }
                adjustments.append(adjustment)
                
                # Update goal in database
                await self.update_goal(user_id, goal.goal_type, new_target, goal.current_value)
                
            elif goal.status == GoalStatus.STAGNANT and days_since_update > 7:
                # Goal hasn't been updated - lower target temporarily
                new_target = goal.target_value * 0.8
                adjustment = {
                    "goal_type": goal.goal_type,
                    "old_target": goal.target_value,
                    "new_target": new_target,
                    "reason": "Goal appears stagnant, making it more achievable",
                    "timestamp": datetime.now().isoformat()
                }
                adjustments.append(adjustment)
                
                await self.update_goal(user_id, goal.goal_type, new_target, goal.current_value)
        
        return {"adjustments": adjustments, "user_id": user_id}
    
    async def update_goal(self, user_id: str, goal_type: str, target_value: float, current_value: float):
        """Update user goal with autonomous adjustment tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get existing goal
        cursor.execute('''
            SELECT adjustment_history FROM user_goals 
            WHERE user_id = ? AND goal_type = ?
        ''', (user_id, goal_type))
        
        result = cursor.fetchone()
        adjustment_history = json.loads(result[0]) if result and result[0] else []
        
        # Add adjustment to history
        adjustment_history.append({
            "timestamp": datetime.now().isoformat(),
            "old_target": target_value,
            "new_target": target_value,
            "trigger": "autonomous_adjustment"
        })
        
        # Determine status
        completion_rate = (current_value / target_value) * 100 if target_value > 0 else 0
        if completion_rate >= 100:
            status = GoalStatus.AHEAD
        elif completion_rate >= 80:
            status = GoalStatus.ON_TRACK
        elif completion_rate >= 50:
            status = GoalStatus.BEHIND
        else:
            status = GoalStatus.STAGNANT
        
        cursor.execute('''
            UPDATE user_goals 
            SET target_value = ?, current_value = ?, status = ?, 
                last_updated = ?, adjustment_history = ?
            WHERE user_id = ? AND goal_type = ?
        ''', (target_value, current_value, status.value, datetime.now(), 
              json.dumps(adjustment_history), user_id, goal_type))
        
        conn.commit()
        conn.close()
    
    async def get_conversation_context(self, user_id: str, conversation_id: str = None) -> ConversationContext:
        """Get or create conversation context for multi-turn conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if conversation_id:
            cursor.execute('''
                SELECT topic, coaching_style, sentiment, messages, created_at, last_active
                FROM conversations WHERE conversation_id = ?
            ''', (conversation_id,))
            
            result = cursor.fetchone()
            if result:
                return ConversationContext(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    topic=result[0],
                    coaching_style=CoachingStyle(result[1]),
                    sentiment=result[2],
                    messages=json.loads(result[3]),
                    created_at=datetime.fromisoformat(result[4]),
                    last_active=datetime.fromisoformat(result[5])
                )
        
        # Create new conversation
        new_conversation_id = f"{user_id}_{int(datetime.now().timestamp())}"
        context = ConversationContext(
            conversation_id=new_conversation_id,
            user_id=user_id,
            topic="nutrition_coaching",
            coaching_style=CoachingStyle.MOTIVATIONAL,
            sentiment="neutral",
            messages=[],
            created_at=datetime.now(),
            last_active=datetime.now()
        )
        
        cursor.execute('''
            INSERT INTO conversations 
            (conversation_id, user_id, topic, coaching_style, sentiment, messages, created_at, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (context.conversation_id, user_id, context.topic, context.coaching_style.value,
              context.sentiment, json.dumps(context.messages), context.created_at, context.last_active))
        
        conn.commit()
        conn.close()
        
        return context
    
    async def analyze_behavior_patterns(self, user_id: str) -> List[BehaviorPattern]:
        """Analyze user behavior patterns for personalized coaching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent interactions
        cursor.execute('''
            SELECT query, response, sentiment, vp_tokens_earned, timestamp, context
            FROM interactions 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''', (user_id,))
        
        interactions = cursor.fetchall()
        patterns = []
        
        if len(interactions) < 5:
            conn.close()
            return patterns
        
        # Analyze timing patterns
        timestamps = [datetime.fromisoformat(i[4]) for i in interactions]
        hours = [t.hour for t in timestamps]
        
        # Find most common interaction hours
        hour_counts = defaultdict(int)
        for hour in hours:
            hour_counts[hour] += 1
        
        if hour_counts:
            peak_hour = max(hour_counts, key=hour_counts.get)
            patterns.append(BehaviorPattern(
                pattern_type="peak_activity_time",
                confidence=0.8,
                frequency=hour_counts[peak_hour],
                last_occurrence=max(timestamps),
                triggers=[f"hour_{peak_hour}"],
                recommendations=[f"Schedule coaching reminders around {peak_hour}:00"]
            ))
        
        # Analyze sentiment trends
        sentiments = [float(i[2]) for i in interactions if i[2]]
        if sentiments:
            avg_sentiment = np.mean(sentiments)
            if avg_sentiment > 0.6:
                patterns.append(BehaviorPattern(
                    pattern_type="positive_engagement",
                    confidence=0.9,
                    frequency=len([s for s in sentiments if s > 0.6]),
                    last_occurrence=max(timestamps),
                    triggers=["positive_feedback", "goal_achievement"],
                    recommendations=["Continue motivational coaching style", "Increase goal challenges"]
                ))
            elif avg_sentiment < 0.4:
                patterns.append(BehaviorPattern(
                    pattern_type="needs_support",
                    confidence=0.8,
                    frequency=len([s for s in sentiments if s < 0.4]),
                    last_occurrence=max(timestamps),
                    triggers=["goal_struggles", "negative_feedback"],
                    recommendations=["Switch to supportive coaching style", "Lower goal targets temporarily"]
                ))
        
        # Save patterns to database
        for pattern in patterns:
            cursor.execute('''
                INSERT OR REPLACE INTO behavior_patterns
                (user_id, pattern_type, confidence, frequency, last_occurrence, triggers, recommendations)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, pattern.pattern_type, pattern.confidence, pattern.frequency,
                  pattern.last_occurrence, json.dumps(pattern.triggers), json.dumps(pattern.recommendations)))
        
        conn.commit()
        conn.close()
        
        return patterns
    
    async def personalized_coaching_response(self, user_id: str, query: str, conversation_id: str = None) -> Dict:
        """Generate personalized coaching response with context awareness"""
        
        # Get user profile and context
        profile = self.get_user_profile(user_id)
        context = await self.get_conversation_context(user_id, conversation_id)
        patterns = await self.analyze_behavior_patterns(user_id)
        
        # Determine coaching style based on patterns
        coaching_style = self.determine_coaching_style(profile, patterns)
        
        # Build comprehensive prompt
        system_message = f"""
        You are FitAgent, an advanced AI nutrition coach with deep personalization capabilities.
        
        COACHING STYLE: {self.coaching_styles[coaching_style]}
        
        USER PROFILE:
        - Total Interactions: {profile['total_interactions']}
        - Success Rate: {profile['success_rate']:.1%}
        - Preferred Style: {profile['coaching_style'].value}
        
        CURRENT GOALS:
        {self.format_goals_for_prompt(profile['goals'])}
        
        BEHAVIOR PATTERNS:
        {self.format_patterns_for_prompt(patterns)}
        
        CONVERSATION CONTEXT:
        - Topic: {context.topic}
        - Previous Messages: {len(context.messages)}
        - Sentiment: {context.sentiment}
        
        INSTRUCTIONS:
        1. Adapt your response to the user's coaching style preference
        2. Reference their specific goals and progress
        3. Consider behavior patterns in your recommendations
        4. Maintain conversation continuity
        5. Provide actionable, personalized advice
        6. Calculate appropriate VP token rewards (10-50 based on engagement quality)
        """
        
        user_prompt = f"""
        User Query: {query}
        
        Provide a comprehensive coaching response that includes:
        1. Personalized analysis based on their profile
        2. Specific recommendations aligned with their goals
        3. Behavioral insights and pattern recognition
        4. VP token calculation with reasoning
        5. Next steps that build on previous interactions
        
        Respond in JSON format with: analysis, recommendations, vp_tokens_earned, progress_update, next_steps, behavior_insights
        """
        
        # Get AI response
        ai_response = await self.call_venice_ai(user_prompt, system_message)
        
        try:
            response_data = json.loads(ai_response)
        except json.JSONDecodeError:
            response_data = {
                "analysis": ai_response,
                "recommendations": ["Continue tracking your nutrition", "Stay consistent with your goals"],
                "vp_tokens_earned": 15,
                "progress_update": {"status": "processed"},
                "next_steps": ["Log your next meal", "Check your progress"],
                "behavior_insights": "Keep building healthy habits!"
            }
        
        # Update conversation context
        context.messages.append({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response_data.get("analysis", ""),
            "coaching_style": coaching_style.value
        })
        
        await self.save_conversation_context(context)
        
        # Record interaction
        await self.record_interaction(user_id, query, response_data, context.conversation_id)
        
        return response_data
    
    def determine_coaching_style(self, profile: Dict, patterns: List[BehaviorPattern]) -> CoachingStyle:
        """Determine optimal coaching style based on user profile and patterns"""
        
        # Check for specific patterns that indicate style preference
        for pattern in patterns:
            if pattern.pattern_type == "positive_engagement" and pattern.confidence > 0.8:
                return CoachingStyle.CHALLENGING
            elif pattern.pattern_type == "needs_support" and pattern.confidence > 0.7:
                return CoachingStyle.SUPPORTIVE
        
        # Default to user's preferred style or motivational
        return profile.get("coaching_style", CoachingStyle.MOTIVATIONAL)
    
    def format_goals_for_prompt(self, goals: List[UserGoal]) -> str:
        """Format goals for AI prompt"""
        if not goals:
            return "No specific goals set"
        
        goal_text = []
        for goal in goals:
            status_emoji = {"on_track": "✅", "ahead": "🚀", "behind": "⚠️", "stagnant": "😴"}.get(goal.status.value, "📊")
            goal_text.append(f"{status_emoji} {goal.goal_type}: {goal.current_value}/{goal.target_value} ({goal.completion_rate:.1f}%)")
        
        return "\n".join(goal_text)
    
    def format_patterns_for_prompt(self, patterns: List[BehaviorPattern]) -> str:
        """Format behavior patterns for AI prompt"""
        if not patterns:
            return "No significant patterns detected yet"
        
        pattern_text = []
        for pattern in patterns:
            pattern_text.append(f"- {pattern.pattern_type}: {pattern.confidence:.1%} confidence, {pattern.frequency} occurrences")
        
        return "\n".join(pattern_text)
    
    async def save_conversation_context(self, context: ConversationContext):
        """Save conversation context to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE conversations 
            SET messages = ?, last_active = ?, sentiment = ?
            WHERE conversation_id = ?
        ''', (json.dumps(context.messages), datetime.now(), context.sentiment, context.conversation_id))
        
        conn.commit()
        conn.close()
    
    async def record_interaction(self, user_id: str, query: str, response_data: Dict, conversation_id: str):
        """Record interaction for behavior analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate sentiment (simplified)
        sentiment = 0.7  # Default positive sentiment
        
        cursor.execute('''
            INSERT INTO interactions 
            (user_id, conversation_id, query, response, sentiment, vp_tokens_earned, timestamp, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, conversation_id, query, response_data.get("analysis", ""), 
              sentiment, response_data.get("vp_tokens_earned", 10), datetime.now(), json.dumps(response_data)))
        
        # Update user profile
        cursor.execute('''
            UPDATE user_profiles 
            SET last_interaction = ?, total_interactions = total_interactions + 1
            WHERE user_id = ?
        ''', (datetime.now(), user_id))
        
        conn.commit()
        conn.close()
    
    async def get_behavioral_insights(self, user_id: str) -> Dict:
        """Generate comprehensive behavioral insights for ASI Alliance prize"""
        profile = self.get_user_profile(user_id)
        patterns = await self.analyze_behavior_patterns(user_id)
        
        insights = {
            "user_id": user_id,
            "total_interactions": profile["total_interactions"],
            "behavior_change_indicators": [],
            "goal_achievement_trends": [],
            "coaching_effectiveness": {},
            "recommendations": []
        }
        
        # Analyze goal achievement trends
        for goal in profile["goals"]:
            trend = {
                "goal_type": goal.goal_type,
                "completion_rate": goal.completion_rate,
                "status": goal.status.value,
                "improvement_rate": self.calculate_improvement_rate(goal),
                "consistency_score": self.calculate_consistency_score(user_id, goal.goal_type)
            }
            insights["goal_achievement_trends"].append(trend)
        
        # Analyze behavior change indicators
        for pattern in patterns:
            if pattern.confidence > 0.7:
                insights["behavior_change_indicators"].append({
                    "pattern": pattern.pattern_type,
                    "strength": pattern.confidence,
                    "frequency": pattern.frequency,
                    "impact": "positive" if "positive" in pattern.pattern_type else "needs_attention"
                })
        
        # Coaching effectiveness
        insights["coaching_effectiveness"] = {
            "engagement_rate": min(1.0, profile["total_interactions"] / 30),  # Normalize to 30 days
            "goal_completion_average": np.mean([g.completion_rate for g in profile["goals"]]) if profile["goals"] else 0,
            "behavior_pattern_strength": np.mean([p.confidence for p in patterns]) if patterns else 0
        }
        
        return insights
    
    def calculate_improvement_rate(self, goal: UserGoal) -> float:
        """Calculate improvement rate for a goal"""
        if not goal.adjustment_history:
            return 0.0
        
        # Simple improvement calculation based on adjustment history
        adjustments = goal.adjustment_history[-5:]  # Last 5 adjustments
        if len(adjustments) < 2:
            return 0.0
        
        # Calculate trend
        values = [adj.get("completion_rate", 0) for adj in adjustments]
        if len(values) >= 2:
            return (values[-1] - values[0]) / len(values)
        
        return 0.0
    
    def calculate_consistency_score(self, user_id: str, goal_type: str) -> float:
        """Calculate consistency score for goal tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get interactions related to this goal type
        cursor.execute('''
            SELECT timestamp FROM interactions 
            WHERE user_id = ? AND (query LIKE ? OR context LIKE ?)
            ORDER BY timestamp DESC LIMIT 30
        ''', (user_id, f"%{goal_type}%", f"%{goal_type}%"))
        
        timestamps = [datetime.fromisoformat(row[0]) for row in cursor.fetchall()]
        conn.close()
        
        if len(timestamps) < 3:
            return 0.0
        
        # Calculate consistency based on interaction frequency
        time_diffs = [(timestamps[i] - timestamps[i+1]).days for i in range(len(timestamps)-1)]
        avg_gap = np.mean(time_diffs)
        
        # Consistency score: lower gaps = higher consistency
        consistency = max(0.0, 1.0 - (avg_gap / 7.0))  # Normalize to weekly consistency
        return min(1.0, consistency)

# Export the enhanced client
enhanced_venice_client = EnhancedVeniceAIClient()
