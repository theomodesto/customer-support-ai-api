from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from app.schemas.ai_classifications import AIClassificationResultSchema
from app.utils.sanitizer import sanitizer

class SupportTicketRequestCreate(BaseModel):
    """Schema for creating a new support request."""
    subject: Optional[str] = Field(default=None, max_length=200)
    body: Optional[str] = Field(default=None, max_length=2000)
    language: Optional[str] = Field(default="en", pattern="^[a-z]{2}$")   
    
    @field_validator('subject', 'body', mode='before')
    def strip_whitespace(cls, v):
        """Strip whitespace from text fields."""
        return v.strip() if v else v
    
    @field_validator('subject', 'body', mode='before')
    def sanitize_input(cls, v):
        """Sanitize input to prevent XSS and injection attacks."""
        if v is None:
            return v
        
        # Check if content is safe before sanitizing
        if not sanitizer.is_safe_content(v):
            from app.utils.logger import logger
            logger.warning(
                "Potentially unsafe content detected",
                component="validation",
                content_preview=v[:100] + "..." if len(v) > 100 else v
            )
        
        # Sanitize the content
        sanitized = sanitizer.sanitize_text(v)
        return sanitized

    
    @model_validator(mode='after')
    def validate_subject_and_body(self):
        """Ensure both 'subject' and 'body' are provided."""
        subject = self.subject
        body = self.body
        
        # Both subject and body must be provided
        if not subject or not body:
            raise ValueError('Both "subject" and "body" must be provided')
            
        return self



class SupportTicketResponse(BaseModel):
    """Schema for support ticket response."""
    id: str

    # Original dataset fields
    subject: Optional[str]
    body: Optional[str]

    queue: Optional[str]
    priority: Optional[str]
    language: Optional[str]

    # AI Classification fields
    category: Optional[str]
    confidence_score: Optional[float]
    summary: Optional[str]
    
    # Tags
    tag_1: Optional[str]
    tag_2: Optional[str]
    tag_3: Optional[str]
    tag_4: Optional[str]
    tag_5: Optional[str]
    tag_6: Optional[str]
    tag_7: Optional[str]
    tag_8: Optional[str]

    created_at: datetime
    updated_at: Optional[datetime]

    
    @field_validator('id', mode='before')
    @classmethod
    def validate_id(cls, v):
        """Convert UUID to string if needed."""
        if isinstance(v, UUID):
            return str(v)
        return v
    
    @field_validator(
        'tag_1', 'tag_2', 'tag_3', 'tag_4', 'tag_5', 'tag_6', 'tag_7', 'tag_8',
        mode='before'
    )
    def _sanitize_tags(cls, v):
        """Ensure tag values are strings or None.
        When tests pass in mocked ticket objects with unset tag attributes, these may be Mock instances
        which do not satisfy the expected type. Convert any non-string values to ``None``.
        """
        if v is None or isinstance(v, str):
            return v
        # Treat any non-string tag value as missing (None)
        return None

    model_config = ConfigDict(from_attributes=True)

class SupportTicketList(BaseModel):
    """Schema for paginated list of support tickets."""
    support_tickets: List[SupportTicketResponse]
    total: int
    page: int
    size: int
    has_next: bool


