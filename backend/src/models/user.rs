use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct User {
    pub id: Uuid,
    pub farcaster_fid: Option<String>,
    pub wallet_address: String,
    pub email: Option<String>,
    pub created_at: DateTime<Utc>,
    pub preferences: UserPreferences,
    pub goals: NutritionGoals,
    pub nft_token_id: Option<String>,
    pub current_level: NFTLevel,
    pub stats: UserStats,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UserPreferences {
    pub dietary_restrictions: Vec<String>,
    pub allergies: Vec<String>,
    pub fitness_goals: Vec<String>,
    pub preferred_meal_times: Vec<String>,
    pub privacy_settings: PrivacySettings,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PrivacySettings {
    pub show_on_leaderboard: bool,
    pub share_achievements: bool,
    pub allow_nft_lending: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NutritionGoals {
    pub daily_protein_grams: f32,
    pub daily_calories: f32,
    pub daily_fiber_grams: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct UserStats {
    pub total_meals_logged: u32,
    pub current_streak: u32,
    pub longest_streak: u32,
    pub total_vp_earned: u32,
    pub average_protein_intake: f32,
    pub goals_completed_this_week: u32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum NFTLevel {
    Seedling = 1,
    Sprout = 2,
    Plant = 3,
    Tree = 4,
    ForestGuardian = 5,
}

#[derive(Debug, Serialize)]
pub struct UserProfileResponse {
    pub success: bool,
    pub data: Option<User>,
    pub error: Option<String>,
}