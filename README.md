# Customer Support AI

A smart customer support system that automatically sorts and handles support tickets using AI. 

## 🚀 Deployment & Usage

### Quick Start (Docker)
# 1. Clone and setup
```bash
git clone <repository>
cd customer-support-ai-api
cp .env.example .env
```

# 2. Start services
```bash
docker-compose --profile dev up -d
```

# 3. Run migrations
```bash
docker exec -it customer_support_api sh -c "alembic upgrade head"
or
docker-compose --profile migrate up
```

# 4. Run seeds db
```bash
docker exec -it customer_support_api sh -c "python ./scripts/seed_db.py"
```

# 4.1 Change the Model 
the default is open_ai you can change to hugging_face
change the .env to 
```env
CLASSIFIER_MODEL=hugging_face
```

# 5. Access applications
# API: http://localhost:8000
# UI: http://localhost:3000
# Docs: http://localhost:8000/docs

# 6. Run test
```bash
docker exec -it customer_support_api sh -c "pytest"
```

### Manual Development Setup
```bash
# Database
docker-compose up --build

# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd ui-react
npm install
npm run dev

# Testing
pytest --cov=app --cov-report=html
```

## What does it do?

- **Smart Sorting**: Automatically categorizes support requests (technical issues, billing questions, general inquiries)
- **Quick Summaries**: Gives you the gist of each request so you can prioritize
- **Confidence Scores**: Shows how sure the AI is about its classification
- **Simple Dashboard**: See all your support stats in one place
- **Real-time**: Processes requests instantly as they come in

## How it works

When someone submits a support request, the AI reads it and figures out:
- What type of issue it is
- How urgent it might be
- A quick summary of the problem

This helps your support team focus on what matters most.

## What you get

- A web API to handle support requests
- A nice web interface to view and manage requests
- Statistics dashboard to track your support trends
- Works with popular AI services (OpenAI, Hugging Face)

## Quick Setup

### The Easy Way (Docker)

1. **Get the code**
```bash
git clone <your-repo-url>
cd customer-support-ai-api
```

2. **Set up your settings**
```bash
cp .env.example .env
# Edit the .env file with your details
```

3. **Start everything**
```bash
docker-compose --profile dev up -d
```

4. **Set up the database**
```bash
docker-compose --profile migrate up
```

5. **Check it out**
   - API: http://localhost:8000
   - Web Interface: http://localhost:3000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (For Developers)

If you prefer to run things manually:

1. **Python setup**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database setup**
```bash
docker-compose up -d customer_support_db
alembic upgrade head
```

3. **Start the API**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **Start the web interface** (optional)
```bash
cd ui-react
npm install
npm run dev
```

5. **Install Bruno API Client**
https://www.usebruno.com/downloads
import ./api-client/Customer Support AI API

## Settings

Create a `.env` file and add your settings:

```env
# Database connection
DATABASE_URL=postgresql://postgres:password@localhost:5432/customer_support_db

# Choose your AI service
CLASSIFIER_MODEL=hugging_face  # or 'openai' or 'fine_tuned_bart'
OPENAI_API_KEY=your_openai_key  # if using OpenAI

# App settings
DEBUG=false
SECRET_KEY=change-this-in-production
```

## AI Options

You can choose from three AI services:

1. **Hugging Face** (free, good quality) - Default choice
2. **OpenAI** (paid, excellent quality) - Needs API key
3. **Fine-tuned Model** (custom trained) - Uses included model

## Testing

Make sure everything works:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

## Using the API

### Create a support request
```bash
curl -X POST "http://localhost:8000/requests" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Can'\''t login to my account",
    "body": "I forgot my password and the reset email isn'\''t working",
    "language": "en"
  }'
```

### Get all technical issues
```bash
curl "http://localhost:8000/requests?category=technical"
```

### Check system stats
```bash
curl "http://localhost:8000/stats"
```

## Project Structure

```
├── app/              # Main API code
├── ui-react/         # Web interface
├── models/           # AI models
├── tests/            # Test files
├── scripts/          # Helper scripts
└── docs/             # Documentation
```

## Common Problems

**Database won't connect?**
```bash
docker-compose ps  # Check if database is running
docker-compose logs customer_support_db  # Check logs
```

**AI not working?**
- Check your `.env` file has the right settings
- Make sure you have internet connection (for Hugging Face/OpenAI)
- Verify your API keys are correct

**Ports already in use?**
```bash
lsof -i :8000  # Check what's using port 8000
lsof -i :3000  # Check what's using port 3000
```

## Production Deployment

For real-world use:

1. Set `DEBUG=false` in your `.env`
2. Use a strong `SECRET_KEY`
3. Set up proper database credentials
4. Configure HTTPS
5. Set up monitoring and backups

## Tech Stack

- **Backend**: FastAPI (Python web framework)
- **Database**: PostgreSQL
- **Frontend**: React
- **AI**: Hugging Face Transformers / OpenAI
- **Deployment**: Docker