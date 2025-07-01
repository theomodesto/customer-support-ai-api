import uuid
from sqlalchemy import Column, Integer, Text, DateTime,  Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
from sqlalchemy.dialects.postgresql import NUMERIC

class AIClassificationResult(Base):
    __tablename__ = "ai_classification_results"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    support_ticket_id = Column(UUID, ForeignKey("support_tickets.id"), index=True)
    
    # AI-generated fields
    category = Column(Text, nullable=False)  # technical, billing, general
    confidence_score = Column(NUMERIC, nullable=False)
    summary = Column(Text, nullable=True)
    priority = Column(Text, nullable=True)

    # Processing metadata
    model_used = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    support_ticket = relationship("SupportTicket", back_populates="ai_classification_result") 