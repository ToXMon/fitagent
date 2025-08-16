use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;
use validator::Validate;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NutritionData {
    pub meal_id: Uuid,
    pub user_id: String,
    pub timestamp: DateTime<Utc>,
    pub image_hash: Option<String>,
    pub food_items: Vec<FoodItem>,
    pub total_nutrition: NutritionSummary,
    pub confidence: f32,
    pub analysis_metadata: AnalysisMetadata,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct FoodItem {
    pub name: String,
    pub confidence: f32,
    pub portion_size: f32, // grams
    pub nutrition_per_100g: NutritionFacts,
    pub estimated_nutrition: NutritionFacts,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NutritionFacts {
    pub calories: f32,
    pub protein: f32,      // grams
    pub carbohydrates: f32, // grams
    pub fat: f32,          // grams
    pub fiber: f32,        // grams
    pub sugar: f32,        // grams
    pub sodium: f32,       // mg
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct NutritionSummary {
    pub total_calories: f32,
    pub total_protein: f32,
    pub total_carbs: f32,
    pub total_fat: f32,
    pub total_fiber: f32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AnalysisMetadata {
    pub processing_time_ms: u64,
    pub model_version: String,
    pub confidence_threshold: f32,
}

#[derive(Debug, Deserialize, Validate)]
pub struct AnalyzePhotoRequest {
    #[validate(length(min = 1))]
    pub image_data: String, // Base64 encoded image
    #[validate(length(min = 1))]
    pub user_id: String,
}

#[derive(Debug, Serialize)]
pub struct NutritionResponse {
    pub success: bool,
    pub data: Option<NutritionData>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DetectedIngredient {
    pub name: String,
    pub confidence: f32,
    pub nutrition_per_100g: NutritionFacts,
    pub estimated_portion_size: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct VisionAnalysisResult {
    pub ingredients: Vec<DetectedIngredient>,
    pub confidence_score: f32,
    pub processing_time_ms: u64,
}