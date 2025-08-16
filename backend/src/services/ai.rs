use reqwest::Client;
use serde_json::json;

use crate::models::{
    CoachingRequest, CoachingAdvice, SuggestedGoal, GoalType, FitAgentError,
    VeniceAIRequest, VeniceAIResponse, VeniceMessage, VeniceParameters
};

pub struct VeniceAIService {
    client: Client,
    api_key: String,
}

impl VeniceAIService {
    pub fn new(api_key: &str) -> Self {
        Self {
            client: Client::new(),
            api_key: api_key.to_string(),
        }
    }

    pub async fn generate_coaching(&self, request: &CoachingRequest) -> Result<CoachingAdvice, FitAgentError> {
        let messages = self.build_message_history(request);
        
        let venice_request = VeniceAIRequest {
            model: "qwen3-235b".to_string(),
            messages,
            temperature: 0.6,
            top_p: 0.95,
            max_tokens: 500,
            venice_parameters: VeniceParameters {
                enable_web_search: "on".to_string(),
                enable_web_citations: true,
                include_venice_system_prompt: true,
            },
        };

        let response = self.client
            .post("https://api.venice.ai/api/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&venice_request)
            .send()
            .await
            .map_err(|e| FitAgentError::ExternalServiceError {
                service: "Venice AI".to_string(),
                message: format!("Network error: {}", e),
            })?;

        if !response.status().is_success() {
            return Err(FitAgentError::AICoachingTimeout {
                cached_response: None,
                message: format!("Venice AI returned status: {}", response.status()),
            });
        }

        let venice_response: VeniceAIResponse = response.json().await
            .map_err(|e| FitAgentError::AICoachingTimeout {
                cached_response: None,
                message: format!("Failed to parse Venice AI response: {}", e),
            })?;

        // Parse the coaching response
        self.parse_coaching_response(venice_response)
    }

    fn build_message_history(&self, request: &CoachingRequest) -> Vec<VeniceMessage> {
        let mut messages = vec![
            VeniceMessage {
                role: "system".to_string(),
                content: self.build_system_prompt(),
            }
        ];

        // Add conversation history if available
        if let Some(history) = &request.conversation_history {
            for msg in history.iter().take(10) { // Limit to last 10 messages
                messages.push(VeniceMessage {
                    role: match msg.message_type {
                        crate::models::MessageType::User => "user".to_string(),
                        crate::models::MessageType::Assistant => "assistant".to_string(),
                        crate::models::MessageType::System => "system".to_string(),
                    },
                    content: msg.content.clone(),
                });
            }
        }

        // Add current nutrition analysis
        let nutrition_summary = format!(
            "Meal Analysis: {} calories, {:.1}g protein, {:.1}g carbs, {:.1}g fat. Foods detected: {}",
            request.nutrition_data.total_nutrition.total_calories,
            request.nutrition_data.total_nutrition.total_protein,
            request.nutrition_data.total_nutrition.total_carbs,
            request.nutrition_data.total_nutrition.total_fat,
            request.nutrition_data.food_items.iter()
                .map(|item| item.name.clone())
                .collect::<Vec<_>>()
                .join(", ")
        );

        messages.push(VeniceMessage {
            role: "user".to_string(),
            content: format!("Please analyze this meal and provide coaching: {}", nutrition_summary),
        });

        messages
    }

    fn build_system_prompt(&self) -> String {
        r#"You are FitAgent, a motivational nutrition coach focused on helping users achieve their daily protein goals and overall health. 

Your personality:
- Encouraging and positive, never judgmental
- Focus on protein intake as the primary goal
- Use scientific knowledge but explain it simply
- Celebrate progress and provide actionable advice
- Suggest realistic next steps

Your response format should be JSON:
{
  "coaching_text": "Your main coaching message (2-3 sentences)",
  "suggested_goal": {
    "goal_type": "DailyProtein",
    "target_value": 25.0,
    "vp_reward": 50,
    "description": "Reach 25g protein in your next meal"
  },
  "motivation_quote": "A short motivational quote",
  "recommendations": ["Specific actionable tip 1", "Specific actionable tip 2"],
  "next_meal_suggestions": ["Food suggestion 1", "Food suggestion 2"]
}

Focus on:
1. Protein content analysis and goals
2. Balanced macro recommendations
3. Encouraging consistency for NFT evolution
4. Practical meal suggestions
5. Celebrating achievements and streaks"#.to_string()
    }

    fn parse_coaching_response(&self, response: VeniceAIResponse) -> Result<CoachingAdvice, FitAgentError> {
        let content = response.choices
            .first()
            .ok_or_else(|| FitAgentError::AICoachingTimeout {
                cached_response: None,
                message: "No response from Venice AI".to_string(),
            })?
            .message
            .content
            .clone();

        // Try to parse as JSON first
        if let Ok(parsed) = serde_json::from_str::<serde_json::Value>(&content) {
            Ok(CoachingAdvice {
                coaching_text: parsed["coaching_text"].as_str().unwrap_or("Great job tracking your meal!").to_string(),
                suggested_goal: Some(SuggestedGoal {
                    goal_type: GoalType::DailyProtein,
                    target_value: parsed["suggested_goal"]["target_value"].as_f64().unwrap_or(25.0) as f32,
                    vp_reward: parsed["suggested_goal"]["vp_reward"].as_u64().unwrap_or(50) as u32,
                    description: parsed["suggested_goal"]["description"].as_str().unwrap_or("Keep up the great work!").to_string(),
                }),
                motivation_quote: parsed["motivation_quote"].as_str().unwrap_or("Every meal is a step toward your goals!").to_string(),
                recommendations: parsed["recommendations"].as_array()
                    .map(|arr| arr.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect())
                    .unwrap_or_else(|| vec!["Keep tracking your meals consistently!".to_string()]),
                next_meal_suggestions: parsed["next_meal_suggestions"].as_array()
                    .map(|arr| arr.iter().filter_map(|v| v.as_str().map(|s| s.to_string())).collect())
                    .unwrap_or_else(|| vec!["Try adding some lean protein to your next meal!".to_string()]),
            })
        } else {
            // Fallback to plain text response
            Ok(CoachingAdvice {
                coaching_text: content,
                suggested_goal: Some(SuggestedGoal {
                    goal_type: GoalType::DailyProtein,
                    target_value: 25.0,
                    vp_reward: 50,
                    description: "Aim for 25g protein in your next meal".to_string(),
                }),
                motivation_quote: "Every healthy choice counts!".to_string(),
                recommendations: vec!["Keep tracking your meals!".to_string()],
                next_meal_suggestions: vec!["Add some lean protein to your next meal".to_string()],
            })
        }
    }
}