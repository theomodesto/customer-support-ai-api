import uuid
from sqlalchemy import JSON, Column, Text, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.dialects.postgresql import NUMERIC
from sqlalchemy import JSON

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    
    # Required fields as per specification
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    
    # Original dataset fields
    queue = Column(Text, nullable=True)
    language = Column(Text, nullable=True)
    
    # AI Classification fields and original dataset fields
    priority = Column(Text, nullable=True)
    
    # AI Classification fields
    category = Column(Text, nullable=True)  # Required field as per specification
    confidence_score = Column(NUMERIC, nullable=True)
    summary = Column(Text, nullable=True)

    # Tags
    tag_1 = Column(Text, nullable=True)
    tag_2 = Column(Text, nullable=True)
    tag_3 = Column(Text, nullable=True)
    tag_4 = Column(Text, nullable=True)
    tag_5 = Column(Text, nullable=True)
    tag_6 = Column(Text, nullable=True)
    tag_7 = Column(Text, nullable=True)
    tag_8 = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    ai_classification_result = relationship("AIClassificationResult", back_populates="support_ticket", uselist=False, cascade="all, delete-orphan")

