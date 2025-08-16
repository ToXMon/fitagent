use actix_web::{post, web, HttpResponse, Result};
use validator::Validate;

use crate::models::{AnalyzePhotoRequest, NutritionResponse, FitAgentError};
use crate::services::vision::VisionService;
use crate::config::AppConfig;

#[post("/analyze-photo")]
pub async fn analyze_photo(
    req: web::Json<AnalyzePhotoRequest>,
    config: web::Data<AppConfig>,
) -> Result<HttpResponse, FitAgentError> {
    // Validate request
    if let Err(validation_errors) = req.validate() {
        return Err(FitAgentError::ValidationError {
            field: "request".to_string(),
            message: format!("Invalid request: {:?}", validation_errors),
        });
    }

    log::info!("Analyzing photo for user: {}", req.user_id);

    // Initialize vision service
    let vision_service = VisionService::new(&config.vision_model_endpoint);

    // Process the image
    match vision_service.analyze_image(&req.image_data, &req.user_id).await {
        Ok(nutrition_data) => {
            log::info!("Photo analysis completed successfully for user: {}", req.user_id);
            Ok(HttpResponse::Ok().json(NutritionResponse {
                success: true,
                data: Some(nutrition_data),
                error: None,
            }))
        }
        Err(e) => {
            log::error!("Photo analysis failed for user {}: {:?}", req.user_id, e);
            Err(e)
        }
    }
}