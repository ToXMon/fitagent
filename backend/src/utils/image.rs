use base64::{Engine as _, engine::general_purpose};
use image::{ImageFormat, DynamicImage};
use std::io::Cursor;
use sha2::{Sha256, Digest};

pub struct ImageProcessor;

impl ImageProcessor {
    pub fn process_base64_image(base64_data: &str) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        // Remove data URL prefix if present
        let clean_data = if base64_data.starts_with("data:image/") {
            base64_data.split(',').nth(1).unwrap_or(base64_data)
        } else {
            base64_data
        };

        // Decode base64
        let image_bytes = general_purpose::STANDARD.decode(clean_data)?;

        // Load and validate image
        let img = image::load_from_memory(&image_bytes)?;

        // Resize if too large (max 1024x1024 for processing efficiency)
        let processed_img = if img.width() > 1024 || img.height() > 1024 {
            img.resize(1024, 1024, image::imageops::FilterType::Lanczos3)
        } else {
            img
        };

        // Convert to JPEG for consistent processing
        let mut output = Vec::new();
        let mut cursor = Cursor::new(&mut output);
        processed_img.write_to(&mut cursor, ImageFormat::Jpeg)?;

        Ok(output)
    }

    pub fn calculate_hash(image_data: &[u8]) -> String {
        let mut hasher = Sha256::new();
        hasher.update(image_data);
        format!("{:x}", hasher.finalize())
    }

    pub fn validate_image_size(image_data: &[u8]) -> Result<(), String> {
        const MAX_SIZE: usize = 10 * 1024 * 1024; // 10MB
        
        if image_data.len() > MAX_SIZE {
            return Err("Image size exceeds 10MB limit".to_string());
        }

        Ok(())
    }

    pub fn validate_image_format(image_data: &[u8]) -> Result<ImageFormat, String> {
        match image::guess_format(image_data) {
            Ok(format) => match format {
                ImageFormat::Jpeg | ImageFormat::Png | ImageFormat::WebP => Ok(format),
                _ => Err("Unsupported image format. Please use JPEG, PNG, or WebP".to_string()),
            },
            Err(_) => Err("Invalid image format".to_string()),
        }
    }
}