use serde::Deserialize;
use std::env;

#[derive(Debug, Clone, Deserialize)]
pub struct AppConfig {
    pub host: String,
    pub port: u16,
    pub venice_ai_key: String,
    pub vision_model_endpoint: String,
    pub tableland_url: Option<String>,
    pub database_url: Option<String>,
}

impl AppConfig {
    pub fn from_env() -> Result<Self, config::ConfigError> {
        // Load from .env file if present
        dotenv::dotenv().ok();

        let config = config::Config::builder()
            .set_default("host", "0.0.0.0")?
            .set_default("port", 8080)?
            .add_source(config::Environment::default())
            .build()?;

        let mut app_config: AppConfig = config.try_deserialize()?;

        // Ensure required environment variables are set
        if app_config.venice_ai_key.is_empty() {
            app_config.venice_ai_key = env::var("VENICE_AI_KEY")
                .expect("VENICE_AI_KEY environment variable is required");
        }

        if app_config.vision_model_endpoint.is_empty() {
            app_config.vision_model_endpoint = env::var("VISION_MODEL_ENDPOINT")
                .unwrap_or_else(|_| "http://localhost:8000".to_string());
        }

        Ok(app_config)
    }
}