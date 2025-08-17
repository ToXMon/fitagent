# FitAgent Frontend Integration Guide

## Current Status
Your uAgent is deployed and running, but it uses the uAgents protocol system which isn't directly accessible via REST API. The `/submit` endpoint you found is just a health check.

## Solution: HTTP REST Wrapper

I've created an HTTP wrapper (`http_wrapper.py`) that provides REST endpoints for your frontend.

## Available API Endpoints

Once you rebuild and redeploy with the new image, you'll have these endpoints:

### Base URL
```
https://90k6i6o5jdbt72i8alpisokh5g.ingress.akashprovid.com:8082
```

### Endpoints

#### 1. Health Check
```http
GET /health
```
Response:
```json
{
  "status": "OK",
  "service": "FitAgent Nutrition Coach"
}
```

#### 2. Nutrition Query (Main Endpoint)
```http
POST /api/nutrition/query
Content-Type: application/json
```

Request Body:
```json
{
  "user_id": "user123",
  "query": "I ate a chicken salad for lunch. How healthy is it?",
  "image_data": "base64_encoded_image_optional",
  "user_goals": {
    "calories": 2000,
    "protein": 150,
    "carbs": 200
  }
}
```

Response:
```json
{
  "success": true,
  "data": {
    "analysis": "Your chicken salad is a great choice...",
    "recommendations": [
      "Add more vegetables for fiber",
      "Consider whole grain croutons",
      "Include healthy fats like avocado"
    ],
    "vp_tokens_earned": 25,
    "progress_update": {
      "calories": 450,
      "protein": 35
    },
    "next_steps": [
      "Log your next meal",
      "Drink more water"
    ]
  }
}
```

#### 3. Get User Context
```http
GET /api/user/{user_id}/context
```

#### 4. Update User Goals
```http
POST /api/user/{user_id}/goals
Content-Type: application/json
```

#### 5. Get User History
```http
GET /api/user/{user_id}/history
```

## Frontend Integration Examples

### JavaScript/React Example
```javascript
// Nutrition query function
async function queryNutrition(userId, query, imageData = null, goals = null) {
  const response = await fetch('https://90k6i6o5jdbt72i8alpisokh5g.ingress.akashprovid.com:8082/api/nutrition/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id: userId,
      query: query,
      image_data: imageData,
      user_goals: goals
    })
  });
  
  const result = await response.json();
  return result;
}

// Usage example
const result = await queryNutrition(
  'user123', 
  'I had oatmeal with berries for breakfast',
  null,
  { calories: 2000, protein: 150 }
);

console.log(result.data.analysis);
console.log(result.data.recommendations);
```

### React Component Example
```jsx
import React, { useState } from 'react';

function NutritionChat() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await fetch('https://90k6i6o5jdbt72i8alpisokh5g.ingress.akashprovid.com:8082/api/nutrition/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'user123',
          query: query
        })
      });
      
      const data = await result.json();
      setResponse(data.data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about your nutrition..."
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Ask FitAgent'}
        </button>
      </form>
      
      {response && (
        <div>
          <h3>Analysis:</h3>
          <p>{response.analysis}</p>
          
          <h3>Recommendations:</h3>
          <ul>
            {response.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
          
          <p>VP Tokens Earned: {response.vp_tokens_earned}</p>
        </div>
      )}
    </div>
  );
}
```

## Next Steps

1. **Start Docker** and rebuild the image:
   ```bash
   docker build --platform linux/amd64 -t wijnaldum/fitagent-nutrition-coach:v3-http .
   docker push wijnaldum/fitagent-nutrition-coach:v3-http
   ```

2. **Redeploy on Akash** using the updated `akash-sdl.yaml`

3. **Test the new endpoints** at port 8082

4. **Integrate with your frontend** using the examples above

The HTTP wrapper maintains all the uAgent functionality while providing REST API access for your frontend.
