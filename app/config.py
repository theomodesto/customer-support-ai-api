import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")

    # Classifier model (hugging_face or open_ai or fine_tuned_bart)
    classifier_model: str = os.getenv("CLASSIFIER_MODEL", "hugging_face")
    
    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    huggingface_token: Optional[str] = os.getenv("HUGGINGFACE_TOKEN")
    
    # Application
    app_name: str = os.getenv("APP_NAME", "Customer Support AI API")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    version: str = "1.0.0"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # AI/ML Settings
    max_text_length: int = int(os.getenv("MAX_TEXT_LENGTH", "5000"))
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))
    
    # Settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings() 