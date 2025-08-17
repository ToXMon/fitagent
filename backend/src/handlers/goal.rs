use actix_web::{post, web, HttpResponse, Result};
use serde::{Deserialize, Serialize};
use validator::Validate;

use crate::models::FitAgentError;
use crate::services::blockchain::BlockchainService;
use crate::config::AppConfig;

#[derive(Debug, Deserialize, Validate)]
pub struct GoalCompletionRequest {
    #[validate(length(min = 1))]
    pub user_id: String,
    pub protein_intake: f32,
    pub calorie_intake: f32,
    pub goal_type: String,
}

#[derive(Debug, Serialize)]
pub struct GoalCompletionResponse {
    pub success: bool,
    pub vp_earned: Option<u32>,
    pub streak_updated: Option<u32>,
    pub nft_evolution: Option<bool>,
    pub error: Option<String>,
}

#[post("/complete-goal")]
pub async fn complete_goal(
    req: web::Json<GoalCompletionRequest>,
    config: web::Data<AppConfig>,
) -> Result<HttpResponse, FitAgentError> {
    // Validate request
    if let Err(validation_errors) = req.validate() {
        return Err(FitAgentError::ValidationError {
            field: "request".to_string(),
            message: format!("Invalid goal completion request: {:?}", validation_errors),
        });
    }

    log::info!("Processing goal completion for user: {}", req.user_id);

    // Initialize blockchain service
    let blockchain_service = BlockchainService::new();

    // Process goal completion
    match blockchain_service.complete_goal(&req.user_id, req.protein_intake, req.calorie_intake).await {
        Ok((vp_earned, streak, nft_evolved)) => {
            log::info!("Goal completion processed successfully for user: {}", req.user_id);
            Ok(HttpResponse::Ok().json(GoalCompletionResponse {
                success: true,
                vp_earned: Some(vp_earned),
                streak_updated: Some(streak),
                nft_evolution: Some(nft_evolved),
                error: None,
            }))
        }
        Err(e) => {
            log::error!("Goal completion failed for user {}: {:?}", req.user_id, e);
            Err(e)
        }
    }
}