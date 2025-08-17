use actix_web::{HttpResponse, ResponseError};
use serde::Serialize;
use std::fmt;

#[derive(Debug, Serialize)]
pub enum FitAgentError {
    VisionAnalysisFailed { 
        confidence: f32, 
        fallback_available: bool,
        message: String,
    },
    AICoachingTimeout { 
        cached_response: Option<String>,
        message: String,
    },
    BlockchainUnavailable { 
        operation_queued: bool,
        message: String,
    },
    RateLimitExceeded { 
        retry_after_seconds: u64,
        message: String,
    },
    ValidationError {
        field: String,
        message: String,
    },
    DatabaseError {
        message: String,
    },
    ExternalServiceError {
        service: String,
        message: String,
    },
    InternalServerError {
        message: String,
    },
}

impl fmt::Display for FitAgentError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            FitAgentError::VisionAnalysisFailed { message, .. } => write!(f, "Vision analysis failed: {}", message),
            FitAgentError::AICoachingTimeout { message, .. } => write!(f, "AI coaching timeout: {}", message),
            FitAgentError::BlockchainUnavailable { message, .. } => write!(f, "Blockchain unavailable: {}", message),
            FitAgentError::RateLimitExceeded { message, .. } => write!(f, "Rate limit exceeded: {}", message),
            FitAgentError::ValidationError { message, .. } => write!(f, "Validation error: {}", message),
            FitAgentError::DatabaseError { message } => write!(f, "Database error: {}", message),
            FitAgentError::ExternalServiceError { service, message } => write!(f, "{} error: {}", service, message),
            FitAgentError::InternalServerError { message } => write!(f, "Internal server error: {}", message),
        }
    }
}

impl ResponseError for FitAgentError {
    fn error_response(&self) -> HttpResponse {
        match self {
            FitAgentError::VisionAnalysisFailed { fallback_available: true, .. } => {
                HttpResponse::PartialContent().json(serde_json::json!({
                    "error": "vision_analysis_failed",
                    "fallback": "manual_entry_available",
                    "message": "We couldn't analyze your photo clearly. You can enter nutrition info manually."
                }))
            }
            FitAgentError::VisionAnalysisFailed { fallback_available: false, .. } => {
                HttpResponse::BadRequest().json(serde_json::json!({
                    "error": "vision_analysis_failed",
                    "message": "Unable to analyze the photo. Please try with a clearer image."
                }))
            }
            FitAgentError::AICoachingTimeout { cached_response: Some(response), .. } => {
                HttpResponse::Ok().json(serde_json::json!({
                    "error": "coaching_timeout",
                    "fallback_response": response,
                    "message": "Using cached coaching response due to timeout."
                }))
            }
            FitAgentError::AICoachingTimeout { cached_response: None, .. } => {
                HttpResponse::ServiceUnavailable().json(serde_json::json!({
                    "error": "coaching_unavailable",
                    "message": "AI coaching is temporarily unavailable. Please try again later."
                }))
            }
            FitAgentError::BlockchainUnavailable { operation_queued: true, .. } => {
                HttpResponse::Accepted().json(serde_json::json!({
                    "error": "blockchain_delayed",
                    "message": "Blockchain operation queued. Rewards will be processed when network is available."
                }))
            }
            FitAgentError::BlockchainUnavailable { operation_queued: false, .. } => {
                HttpResponse::ServiceUnavailable().json(serde_json::json!({
                    "error": "blockchain_unavailable",
                    "message": "Blockchain services are temporarily unavailable."
                }))
            }
            FitAgentError::RateLimitExceeded { retry_after_seconds, .. } => {
                HttpResponse::TooManyRequests()
                    .insert_header(("Retry-After", retry_after_seconds.to_string()))
                    .json(serde_json::json!({
                        "error": "rate_limit_exceeded",
                        "retry_after_seconds": retry_after_seconds,
                        "message": "Too many requests. Please try again later."
                    }))
            }
            FitAgentError::ValidationError { field, message } => {
                HttpResponse::BadRequest().json(serde_json::json!({
                    "error": "validation_error",
                    "field": field,
                    "message": message
                }))
            }
            FitAgentError::DatabaseError { message } => {
                HttpResponse::InternalServerError().json(serde_json::json!({
                    "error": "database_error",
                    "message": "Database operation failed."
                }))
            }
            FitAgentError::ExternalServiceError { service, message } => {
                HttpResponse::BadGateway().json(serde_json::json!({
                    "error": "external_service_error",
                    "service": service,
                    "message": format!("{} service is unavailable.", service)
                }))
            }
            FitAgentError::InternalServerError { message } => {
                HttpResponse::InternalServerError().json(serde_json::json!({
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred."
                }))
            }
        }
    }
}