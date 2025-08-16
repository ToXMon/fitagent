# FitAgent Backend

High-performance Rust backend for the FitAgent MVP, built with Actix-web for ETHGlobal New York 2025.

## Architecture

- **Framework**: Actix-web for HTTP server
- **AI Integration**: Venice AI (qwen3-235b) for nutrition coaching
- **Vision**: Fine-tuned ViT model on Akash Network
- **Blockchain**: Base (CDP) + Flow (NFTs) integration
- **Database**: Tableland for conversation history

## API Endpoints

### Health Check
```
GET /api/health
```

### Photo Analysis
```
POST /api/analyze-photo
Content-Type: application/json

{
  "image_data": "base64_encoded_image",
  "user_id": "user_identifier"
}
```

### AI Coaching
```
POST /api/coach-meal
Content-Type: application/json

{
  "user_id": "user_identifier",
  "nutrition_data": { ... },
  "conversation_history": [ ... ]
}
```

### User Profile
```
GET /api/user/profile/{user_id}
```

### Goal Completion
```
POST /api/complete-goal
Content-Type: application/json

{
  "user_id": "user_identifier",
  "protein_intake": 25.5,
  "calorie_intake": 450.0,
  "goal_type": "daily_protein"
}
```

## Development Setup

1. **Install Rust** (if not already installed):
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

2. **Clone and setup**:
   ```bash
   cd fitagent-mvp/backend
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run development server**:
   ```bash
   cargo run
   ```

4. **Run tests**:
   ```bash
   cargo test
   ```

## Environment Variables

Required:
- `VENICE_AI_KEY`: Venice AI API key for coaching
- `VISION_MODEL_ENDPOINT`: URL of fine-tuned ViT model

Optional:
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8080)
- `TABLELAND_URL`: Tableland API endpoint
- `RUST_LOG`: Logging level (default: info)

## Docker Deployment

### Build Image
```bash
docker build -t fitagent-backend .
```

### Run Container
```bash
docker run -p 8080:8080 \
  -e VENICE_AI_KEY=your_key \
  -e VISION_MODEL_ENDPOINT=http://your-model-endpoint \
  fitagent-backend
```

## Akash Network Deployment

The backend is designed for deployment on Akash Network for decentralized scaling:

```yaml
# akash-deployment.yml
version: "2.0"
services:
  fitagent-backend:
    image: fitagent/backend:latest
    expose:
      - port: 8080
        as: 80
        to:
          - global: true
    env:
      - VENICE_AI_KEY=encrypted_key
      - VISION_MODEL_ENDPOINT=http://vision-service
    resources:
      cpu:
        units: 2
      memory:
        size: 4Gi
      storage:
        size: 10Gi
```

## Performance Features

- **Async/Await**: Full async processing with Tokio runtime
- **Connection Pooling**: Efficient HTTP client reuse
- **Error Handling**: Comprehensive error types with fallbacks
- **Rate Limiting**: Built-in rate limiting with Governor
- **Image Processing**: Optimized image handling with compression
- **Caching**: Response caching for AI coaching (planned)

## Security

- **Input Validation**: Comprehensive request validation
- **CORS**: Configurable CORS policies
- **Rate Limiting**: Protection against abuse
- **Error Sanitization**: Safe error messages for production
- **Image Validation**: File type and size validation

## Monitoring

- **Health Checks**: Built-in health endpoint
- **Logging**: Structured logging with env_logger
- **Metrics**: Performance metrics collection (planned)
- **Tracing**: Request tracing for debugging

## Prize Integration

### Flow Prize ($20K)
- Cross-chain NFT evolution triggers
- Flow blockchain integration for dynamic NFTs

### ASI Alliance Prize ($10K)
- Venice AI integration for autonomous coaching
- Conversation history and context management

### CDP Prize ($20K)
- Base network smart contract integration
- VP token minting and streaming rewards

### Privy Prize ($5K)
- Seamless wallet integration support
- User profile and blockchain interaction

## Development Roadmap

### Phase 1 (Current)
- [x] Basic Actix-web server setup
- [x] API endpoint structure
- [x] Venice AI integration
- [x] Vision model integration
- [x] Error handling system

### Phase 2 (Next)
- [ ] Tableland database integration
- [ ] Blockchain service implementation
- [ ] Rate limiting and caching
- [ ] Comprehensive testing

### Phase 3 (Future)
- [ ] Performance optimization
- [ ] Advanced monitoring
- [ ] Production deployment
- [ ] Scaling improvements

## Contributing

1. Follow Rust best practices and clippy suggestions
2. Add tests for new functionality
3. Update documentation for API changes
4. Use conventional commit messages

## License

MIT License - see LICENSE file for details.