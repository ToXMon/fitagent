use actix_web::{get, web, HttpResponse, Result};

use crate::models::{UserProfileResponse, FitAgentError};
use crate::services::user::UserService;
use crate::config::AppConfig;

#[get("/user/profile/{user_id}")]
pub async fn get_user_profile(
    path: web::Path<String>,
    config: web::Data<AppConfig>,
) -> Result<HttpResponse, FitAgentError> {
    let user_id = path.into_inner();
    
    log::info!("Fetching profile for user: {}", user_id);

    // Initialize user service
    let user_service = UserService::new();

    // Get user profile
    match user_service.get_profile(&user_id).await {
        Ok(user) => {
            log::info!("User profile retrieved successfully for: {}", user_id);
            Ok(HttpResponse::Ok().json(UserProfileResponse {
                success: true,
                data: Some(user),
                error: None,
            }))
        }
        Err(e) => {
            log::error!("Failed to retrieve user profile for {}: {:?}", user_id, e);
            Err(e)
        }
    }
}