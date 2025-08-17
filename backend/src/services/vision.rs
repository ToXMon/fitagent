use reqwest::Client;
use serde_json::json;
use std::time::Instant;
use uuid::Uuid;
use chrono::Utc;

use crate::models::{
    NutritionData, FoodItem, NutritionFacts, NutritionSummary, 
    AnalysisMetadata, VisionAnalysisResult, DetectedIngredient, FitAgentError
};
use crate::utils::image::ImageProcessor;

pub struct VisionService {
    client: Client,
    endpoint: String,
}

impl VisionService {
    pub fn new(endpoint: &str) -> Self {
        Self {
            client: Client::new(),
            endpoint: endpoint.to_string(),
        }
    }

    pub async fn analyze_image(&self, image_data: &str, user_id: &str) -> Result<NutritionData, FitAgentError> {
        let start_time = Instant::now();

        // Process and validate image
        let processed_image = ImageProcessor::process_base64_image(image_data)
            .map_err(|e| FitAgentError::VisionAnalysisFailed {
                confidence: 0.0,
                fallback_available: true,
                message: format!("Image processing failed: {}", e),
            })?;

        // Call fine-tuned ViT model
        let vision_result = self.call_vision_model(&processed_image).await?;

        // Convert vision results to nutrition data
        let food_items = self.convert_to_food_items(vision_result.ingredients);
        let total_nutrition = self.calculate_total_nutrition(&food_items);

        let processing_time = start_time.elapsed().as_millis() as u64;

        Ok(NutritionData {
            meal_id: Uuid::new_v4(),
            user_id: user_id.to_string(),
            timestamp: Utc::now(),
            image_hash: Some(ImageProcessor::calculate_hash(&processed_image)),
            food_items,
            total_nutrition,
            confidence: vision_result.confidence_score,
            analysis_metadata: AnalysisMetadata {
                processing_time_ms: processing_time,
                model_version: "fitagent-vit-v1.0".to_string(),
                confidence_threshold: 0.8,
            },
        })
    }

    async fn call_vision_model(&self, image_data: &[u8]) -> Result<VisionAnalysisResult, FitAgentError> {
        let payload = json!({
            "image": base64::encode(image_data),
            "confidence_threshold": 0.8,
            "max_detections": 10
        });

        let response = self.client
            .post(&format!("{}/analyze", self.endpoint))
            .json(&payload)
            .send()
            .await
            .map_err(|e| FitAgentError::ExternalServiceError {
                service: "Vision Model".to_string(),
                message: format!("Network error: {}", e),
            })?;

        if !response.status().is_success() {
            return Err(FitAgentError::VisionAnalysisFailed {
                confidence: 0.0,
                fallback_available: true,
                message: format!("Vision model returned status: {}", response.status()),
            });
        }

        let vision_result: VisionAnalysisResult = response.json().await
            .map_err(|e| FitAgentError::VisionAnalysisFailed {
                confidence: 0.0,
                fallback_available: true,
                message: format!("Failed to parse vision model response: {}", e),
            })?;

        // Check if confidence is above threshold
        if vision_result.confidence_score < 0.8 {
            return Err(FitAgentError::VisionAnalysisFailed {
                confidence: vision_result.confidence_score,
                fallback_available: true,
                message: "Low confidence in food detection".to_string(),
            });
        }

        Ok(vision_result)
    }

    fn convert_to_food_items(&self, ingredients: Vec<DetectedIngredient>) -> Vec<FoodItem> {
        ingredients.into_iter().map(|ingredient| {
            let estimated_nutrition = NutritionFacts {
                calories: ingredient.nutrition_per_100g.calories * (ingredient.estimated_portion_size / 100.0),
                protein: ingredient.nutrition_per_100g.protein * (ingredient.estimated_portion_size / 100.0),
                carbohydrates: ingredient.nutrition_per_100g.carbohydrates * (ingredient.estimated_portion_size / 100.0),
                fat: ingredient.nutrition_per_100g.fat * (ingredient.estimated_portion_size / 100.0),
                fiber: ingredient.nutrition_per_100g.fiber * (ingredient.estimated_portion_size / 100.0),
                sugar: ingredient.nutrition_per_100g.sugar * (ingredient.estimated_portion_size / 100.0),
                sodium: ingredient.nutrition_per_100g.sodium * (ingredient.estimated_portion_size / 100.0),
            };

            FoodItem {
                name: ingredient.name,
                confidence: ingredient.confidence,
                portion_size: ingredient.estimated_portion_size,
                nutrition_per_100g: ingredient.nutrition_per_100g,
                estimated_nutrition,
            }
        }).collect()
    }

    fn calculate_total_nutrition(&self, food_items: &[FoodItem]) -> NutritionSummary {
        let mut total = NutritionSummary {
            total_calories: 0.0,
            total_protein: 0.0,
            total_carbs: 0.0,
            total_fat: 0.0,
            total_fiber: 0.0,
        };

        for item in food_items {
            total.total_calories += item.estimated_nutrition.calories;
            total.total_protein += item.estimated_nutrition.protein;
            total.total_carbs += item.estimated_nutrition.carbohydrates;
            total.total_fat += item.estimated_nutrition.fat;
            total.total_fiber += item.estimated_nutrition.fiber;
        }

        total
    }
}