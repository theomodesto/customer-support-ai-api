from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
from app.schemas.enums import CategoryEnum

class AIClassificationResultSchema(BaseModel):
    """Schema for AI classification results."""
    id: str
    support_ticket_id: str

    # AI-generated fields
    category: CategoryEnum
    confidence_score: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None

    # Original and AI Classification fields
    priority: Optional[str] = None

    # Processing metadata
    model_used: Optional[str] = None    

    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime]
    
    @field_validator('id', 'support_ticket_id', mode='before')
    @classmethod
    def validate_uuid_fields(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, UUID):
            return str(v)
        return v
    
    model_config = ConfigDict(from_attributes=True) 


class AIClassifierSchema(BaseModel):
    """Schema for creating AI classification results."""
    priority: Optional[str] = Field(default="medium")
    category: Optional[CategoryEnum] = Field(default=CategoryEnum.general)
    confidence_score: Optional[float] = Field(default=0.0)
    summary: Optional[str] = Field(default="")
    model_used: Optional[str] = None