# Feedback Insights Backend

A backend system that collects conversation summaries from ElevenLabs Voice Agent APIs and generates actionable insights for product owners to understand how their features and products are performing.

## Features

- 🎙️ **ElevenLabs Integration**: Automatically fetch conversation data from ElevenLabs Voice Agent APIs
- 📊 **Intelligent Analysis**: Generate insights using NLP and sentiment analysis
- 🔍 **Topic Extraction**: Identify key themes and topics from user feedback
- 📈 **Trend Analysis**: Track sentiment and feedback trends over time
- 🚀 **RESTful API**: Clean API endpoints for data access and visualization
- 🔄 **Webhook Support**: Real-time conversation processing via webhooks
- ⚡ **Public APIs**: No authentication required for easy demo access

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database configuration
   ```

3. **Start the Server**
   ```bash
   uvicorn start:app --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once running, visit `http://localhost:8000/docs` for interactive API documentation.

## Environment Variables

- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `DATABASE_URL`: PostgreSQL connection string (SQLite used locally)
- `OPENAI_API_KEY`: OpenAI API key for enhanced NLP processing (optional)

## Architecture

```
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core configuration and settings
│   ├── db/           # Database connection and session management
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic schemas for request/response validation
│   ├── services/     # Business logic and external API integrations
│   └── utils/        # Utility functions and helpers
├── tests/            # Test suite
└── alembic/          # Database migration files
```

## Deployment

Ready for deployment on Railway, Replit, or similar platforms with included configuration files.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request
