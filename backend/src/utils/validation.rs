use validator::{Validate, ValidationError};

pub fn validate_user_id(user_id: &str) -> Result<(), ValidationError> {
    if user_id.is_empty() {
        return Err(ValidationError::new("User ID cannot be empty"));
    }
    
    if user_id.len() > 100 {
        return Err(ValidationError::new("User ID too long"));
    }
    
    Ok(())
}

pub fn validate_protein_intake(protein: f32) -> Result<(), ValidationError> {
    if protein < 0.0 {
        return Err(ValidationError::new("Protein intake cannot be negative"));
    }
    
    if protein > 500.0 {
        return Err(ValidationError::new("Protein intake seems unrealistic"));
    }
    
    Ok(())
}

pub fn validate_calorie_intake(calories: f32) -> Result<(), ValidationError> {
    if calories < 0.0 {
        return Err(ValidationError::new("Calorie intake cannot be negative"));
    }
    
    if calories > 10000.0 {
        return Err(ValidationError::new("Calorie intake seems unrealistic"));
    }
    
    Ok(())
}

pub fn validate_base64_image(data: &str) -> Result<(), ValidationError> {
    if data.is_empty() {
        return Err(ValidationError::new("Image data cannot be empty"));
    }
    
    // Check if it's a valid base64 string
    let clean_data = if data.starts_with("data:image/") {
        data.split(',').nth(1).unwrap_or(data)
    } else {
        data
    };
    
    if base64::decode(clean_data).is_err() {
        return Err(ValidationError::new("Invalid base64 image data"));
    }
    
    Ok(())
}