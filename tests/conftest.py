import pytest
import asyncio
from typing import Generator
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.repository.support_ticket_repo import SupportTicketRepo
from app.repository.ai_classification_results_repo import AIClassificationResultRepo
from app.services.ai_classifier import AIClassifier

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the database tables once for the test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Category: technical\nConfidence: 0.85\nSummary: Technical issue with server connectivity."
                }
            }
        ]
    }


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client."""
    with patch('openai.chat.completions.create') as mock_create:
        mock_create.return_value = Mock(**mock_openai_response)
        yield mock_create


@pytest.fixture
def sample_dataset_tickets():
    """Sample dataset tickets for testing."""
    return [
        {
            "text": "Server crashed with memory error",
            "queue": "Technical Support",
            "priority": "Critical",
            "answer": "Restarted the server and increased memory allocation.",
            "expected_category": "technical",
            "expected_confidence": 0.9
        },
        {
            "text": "I was overcharged on my invoice",
            "queue": "Billing and Payments",
            "priority": "Medium",
            "answer": "Processed refund for the overcharge.",
            "expected_category": "billing",
            "expected_confidence": 0.7
        },
        {
            "text": "General inquiry about services",
            "queue": "Customer Service",
            "priority": "Low",
            "answer": "Provided information about our services.",
            "expected_category": "general",
            "expected_confidence": 0.5
        }
    ]


@pytest.fixture
def ai_classifier():
    """Create AI classifier instance for testing."""
    return ai_classifier


@pytest.fixture
def support_ticket_repo():
    """Create support ticket repository instance."""
    return SupportTicketRepo


@pytest.fixture
def ai_classification_repo():
    """Create AI classification results repository instance."""
    return AIClassificationResultRepo


@pytest.fixture
def test_support_ticket_data():
    """Sample support ticket data for testing."""
    return {
        "subject": "Test Support Ticket",
        "body": "This is a test support ticket for testing purposes.",
        "customer_email": "test@example.com",
        "priority": "Medium"
    }


@pytest.fixture
def test_classification_result():
    """Sample classification result data for testing."""
    return {
        "category": "technical",
        "confidence_score": 0.85,
        "summary": "Technical issue with server connectivity.",
        "model_used": "openai_gpt",
        "processing_time_ms": 150
    } 