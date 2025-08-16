use actix_cors::Cors;
use actix_web::{web, App, HttpServer, Result};
use env_logger::Env;

mod config;
mod handlers;
mod models;
mod services;
mod utils;

use config::AppConfig;
use handlers::{health, photo, coaching, user, goal};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Initialize logger
    env_logger::init_from_env(Env::default().default_filter_or("info"));

    // Load configuration
    let config = AppConfig::from_env().expect("Failed to load configuration");
    let bind_address = format!("{}:{}", config.host, config.port);

    log::info!("Starting FitAgent backend server on {}", bind_address);

    // Start HTTP server
    HttpServer::new(move || {
        let cors = Cors::default()
            .allow_any_origin()
            .allow_any_method()
            .allow_any_header()
            .max_age(3600);

        App::new()
            .app_data(web::Data::new(config.clone()))
            .wrap(cors)
            .wrap(actix_web::middleware::Logger::default())
            .service(
                web::scope("/api")
                    .service(health::health_check)
                    .service(photo::analyze_photo)
                    .service(coaching::coach_meal)
                    .service(user::get_user_profile)
                    .service(goal::complete_goal)
            )
    })
    .bind(&bind_address)?
    .run()
    .await
}