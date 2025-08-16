use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;
use validator::Validate;

use super::nutrition::NutritionData;

#[derive(Debug, Deserialize, Validate)]
pub struct CoachingRequest {
    #[validate(length(min = 1))]
    pub user_id: String,
    pub nutrition_data: NutritionData,
    pub conversation_history: Option<Vec<Message>>,
    pub user_preferences: Option<UserCoachingPreferences>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Message {
    pub id: Uuid,
    pub message_type: MessageType,
    pub content: String,
    pub timestamp: DateTime<Utc>,
    pub metadata: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum MessageType {
    User,
    Assistant,
    System,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UserCoachingPreferences {
    pub coaching_style: CoachingStyle,
    pub focus_areas: Vec<FocusArea>,
    pub motivation_level: MotivationLevel,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum CoachingStyle {
    Encouraging,
    Direct,
    Scientific,
    Casual,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum FocusArea {
    Protein,
    Calories,
    Macros,
    Micronutrients,
    PortionControl,
    MealTiming,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum MotivationLevel {
    Low,
    Medium,
    High,
}

#[derive(Debug, Serialize)]
pub struct CoachingResponse {
    pub success: bool,
    pub data: Option<CoachingAdvice>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CoachingAdvice {
    pub coaching_text: String,
    pub suggested_goal: Option<SuggestedGoal>,
    pub motivation_quote: String,
    pub recommendations: Vec<String>,
    pub next_meal_suggestions: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct SuggestedGoal {
    pub goal_type: GoalType,
    pub target_value: f32,
    pub vp_reward: u32,
    pub description: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum GoalType {
    DailyProtein,
    DailyCalories,
    MealBalance,
    Hydration,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceAIRequest {
    pub model: String,
    pub messages: Vec<VeniceMessage>,
    pub temperature: f32,
    pub top_p: f32,
    pub max_tokens: u32,
    pub venice_parameters: VeniceParameters,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceMessage {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceParameters {
    pub enable_web_search: String,
    pub enable_web_citations: bool,
    pub include_venice_system_prompt: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceAIResponse {
    pub choices: Vec<VeniceChoice>,
    pub usage: Option<VeniceUsage>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceChoice {
    pub message: VeniceMessage,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VeniceUsage {
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub total_tokens: u32,
}