# Security & Best Practices

## Implemented Security Measures

### 1. Input Validation

The API implements comprehensive input validation using Pydantic schemas:

- **Field Constraints**: Maximum length limits (5000 chars for text, 500 for subject)
- **Type Validation**: UUID validation, datetime handling, optional field management
- **Custom Validators**: Whitespace stripping, text/subject-body validation logic
- **Schema Validation**: Automatic request/response validation

```python
# Example from app/schemas/support_tickets.py
class SupportTicketRequestCreate(BaseModel):
    text: Optional[str] = Field(default=None, max_length=5000)
    subject: Optional[str] = Field(default=None, max_length=500)
    body: Optional[str] = Field(default=None, max_length=5000)
```

### 2. Secret Management

All sensitive configuration is managed through environment variables:

- **API Keys**: OpenAI, HuggingFace tokens via environment
- **Database Credentials**: Connection strings via `DATABASE_URL`
- **Application Secrets**: Secret keys for JWT/sessions
- **Git Protection**: `.env` files excluded from version control

```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@host:port/db
OPENAI_API_KEY=sk-...
HUGGINGFACE_TOKEN=hf_...
SECRET_KEY=your-secret-key-change-in-production
```

### 3. Error Management

Comprehensive error handling with security considerations:

- **Generic Client Errors**: Proper HTTP status codes (400, 404, 422, 500)
- **Structured Error Responses**: Consistent error format with detail and error_code
- **Global Exception Handler**: Production-safe error messages
- **Debug Mode Protection**: Detailed errors only in development

```python
# Production error response (debug=False)
{"detail": "Internal server error"}

# Development error response (debug=True)
{
    "detail": "Internal server error: Database connection failed",
    "error_type": "DatabaseError"
}
```

### 4. Data Privacy

Data privacy measures implemented:

- **English-Only Processing**: Dataset filtered to English tickets only
- **Language Tracking**: Database schema includes language field
- **Consistent Language Handling**: All sample data marked as "en"
- **Multi-language Model Drift Prevention**: Focus on English for model consistency

### 5. Production Considerations

Production-ready features:

- **Configuration Management**: Environment-based settings
- **Database Migrations**: Alembic for schema versioning
- **Docker Support**: Containerized deployment ready
- **Health Checks**: `/health` endpoint for monitoring
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## Authentication Strategy (Planned)

### Current State
The API currently operates without authentication for development and demonstration purposes.

### Planned Implementation

#### 1. JWT-Based Authentication
```python
# Planned authentication middleware
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### 2. API Key Authentication (Alternative)
For service-to-service communication:
```python
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

#### 3. Role-Based Access Control
```python
# Planned role definitions
class UserRole(str, Enum):
    ADMIN = "admin"
    SUPPORT_AGENT = "support_agent"
    READ_ONLY = "read_only"

def require_role(required_role: UserRole):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
```

### Implementation Priority
1. **Phase 1**: JWT authentication for all endpoints
2. **Phase 2**: Role-based access control
3. **Phase 3**: API key authentication for external services
4. **Phase 4**: Rate limiting and request throttling

## Additional Security Recommendations

### 1. Input Sanitization
```python
import html
import re

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Escape HTML entities
    text = html.escape(text)
    # Remove script tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE)
    return text.strip()
```

### 2. Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_ml_error(self, error: Exception, context: dict):
        """Log ML processing errors with structured data."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "component": "ai_classification",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        self.logger.error(json.dumps(log_entry))
```

### 3. Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request, exc):
    return _rate_limit_exceeded_handler(request, exc)

@router.post("")
@limiter.limit("10/minute")
async def create_support_request(request, db):
    # Implementation
    pass
```

### 4. CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Security Checklist for Production

- [ ] Implement JWT authentication
- [ ] Add input sanitization
- [ ] Implement structured logging
- [ ] Configure rate limiting
- [ ] Set up CORS policies
- [ ] Enable HTTPS/TLS
- [ ] Configure database connection pooling
- [ ] Set up monitoring and alerting
- [ ] Implement backup strategies
- [ ] Configure firewall rules
- [ ] Set up intrusion detection
- [ ] Regular security audits
