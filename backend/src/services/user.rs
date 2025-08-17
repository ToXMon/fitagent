use uuid::Uuid;
use chrono::Utc;

use crate::models::{
    User, UserPreferences, NutritionGoals, UserStats, NFTLevel, 
    PrivacySettings, FitAgentError
};

pub struct UserService {
    // In a real implementation, this would have database connections
}

impl UserService {
    pub fn new() -> Self {
        Self {}
    }

    pub async fn get_profile(&self, user_id: &str) -> Result<User, FitAgentError> {
        // For MVP, return a mock user profile
        // In production, this would query Tableland or another database
        
        log::info!("Fetching user profile for: {}", user_id);

        // Mock user data for demonstration
        Ok(User {
            id: Uuid::parse_str(user_id).unwrap_or_else(|_| Uuid::new_v4()),
            farcaster_fid: Some("12345".to_string()),
            wallet_address: "0x742d35Cc6634C0532925a3b8D4C9db96590c6C8b".to_string(),
            email: Some("user@example.com".to_string()),
            created_at: Utc::now(),
            preferences: UserPreferences {
                dietary_restrictions: vec!["vegetarian".to_string()],
                allergies: vec!["nuts".to_string()],
                fitness_goals: vec!["muscle_gain".to_string(), "weight_loss".to_string()],
                preferred_meal_times: vec!["7:00".to_string(), "12:00".to_string(), "18:00".to_string()],
                privacy_settings: PrivacySettings {
                    show_on_leaderboard: true,
                    share_achievements: true,
                    allow_nft_lending: true,
                },
            },
            goals: NutritionGoals {
                daily_protein_grams: 120.0,
                daily_calories: 2000.0,
                daily_fiber_grams: 25.0,
            },
            nft_token_id: Some("1".to_string()),
            current_level: NFTLevel::Sprout,
            stats: UserStats {
                total_meals_logged: 45,
                current_streak: 7,
                longest_streak: 14,
                total_vp_earned: 2250,
                average_protein_intake: 95.5,
                goals_completed_this_week: 5,
            },
        })
    }

    pub async fn create_user(&self, wallet_address: &str, farcaster_fid: Option<String>) -> Result<User, FitAgentError> {
        log::info!("Creating new user with wallet: {}", wallet_address);

        let new_user = User {
            id: Uuid::new_v4(),
            farcaster_fid,
            wallet_address: wallet_address.to_string(),
            email: None,
            created_at: Utc::now(),
            preferences: UserPreferences {
                dietary_restrictions: vec![],
                allergies: vec![],
                fitness_goals: vec!["general_health".to_string()],
                preferred_meal_times: vec!["8:00".to_string(), "12:00".to_string(), "19:00".to_string()],
                privacy_settings: PrivacySettings {
                    show_on_leaderboard: false, // Default to private
                    share_achievements: false,
                    allow_nft_lending: false,
                },
            },
            goals: NutritionGoals {
                daily_protein_grams: 100.0, // Default protein goal
                daily_calories: 2000.0,
                daily_fiber_grams: 25.0,
            },
            nft_token_id: None, // Will be set when NFT is minted
            current_level: NFTLevel::Seedling,
            stats: UserStats {
                total_meals_logged: 0,
                current_streak: 0,
                longest_streak: 0,
                total_vp_earned: 0,
                average_protein_intake: 0.0,
                goals_completed_this_week: 0,
            },
        };

        // In production, save to database here
        
        Ok(new_user)
    }

    pub async fn update_user_stats(&self, user_id: &str, protein_intake: f32, goal_completed: bool) -> Result<(), FitAgentError> {
        log::info!("Updating stats for user: {}", user_id);
        
        // In production, this would update the database
        // For now, just log the operation
        log::info!("User {} stats updated: protein={}, goal_completed={}", user_id, protein_intake, goal_completed);
        
        Ok(())
    }
}