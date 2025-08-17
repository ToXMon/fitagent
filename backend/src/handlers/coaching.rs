use actix_web::{post, web, HttpResponse, Result};
use validator::Validate;

use crate::models::{CoachingRequest, CoachingResponse, FitAgentError};
use crate::services::ai::VeniceAIService;
use crate::config::AppConfig;

#[post("/coach-meal")]
pub async fn coach_meal(
    req: web::Json<CoachingRequest>,
    config: web::Data<AppConfig>,
) -> Result<HttpResponse, FitAgentError> {
    // Validate request
    if let Err(validation_errors) = req.validate() {
        return Err(FitAgentError::ValidationError {
            field: "request".to_string(),
            message: format!("Invalid coaching request: {:?}", validation_errors),
        });
    }

    log::info!("Generating coaching advice for user: {}", req.user_id);

    // Initialize AI service
    let ai_service = VeniceAIService::new(&config.venice_ai_key);

    // Generate coaching advice
    match ai_service.generate_coaching(&req).await {
        Ok(coaching_advice) => {
            log::info!("Coaching advice generated successfully for user: {}", req.user_id);
            Ok(HttpResponse::Ok().json(CoachingResponse {
                success: true,
                data: Some(coaching_advice),
                error: None,
            }))
        }
        Err(e) => {
            log::error!("Coaching generation failed for user {}: {:?}", req.user_id, e);
            Err(e)
        }
    }
}