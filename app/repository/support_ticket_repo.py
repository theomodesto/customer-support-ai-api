from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
from app.models.support_ticket import SupportTicket
from app.schemas.support_tickets import SupportTicketRequestCreate
from app.utils.logger import logger

class SupportTicketRepo:
    """Service for database operations on support tickets."""
    
    @staticmethod
    def create_support_ticket(
        db: Session, 
        request: SupportTicketRequestCreate,
        **kwargs
    ) -> SupportTicket:
        """Create a new support ticket."""
        try:
            subject = request.subject
            body = request.body

            # Create ticket
            support_ticket = SupportTicket(
                subject=subject,
                body=body,
                language=request.language,
                **kwargs
            )
            
            db.add(support_ticket)
            db.commit()
            db.refresh(support_ticket)
            return support_ticket
        except Exception as e:
            db.rollback()
            logger.log_database_operation(
                operation="create_support_ticket",
                table="support_tickets",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e

    
    @staticmethod
    def get_support_ticket_by_id(db: Session, support_ticket_id: str) -> Optional[SupportTicket]:
        """Get a support ticket by ID with AI classification."""
        try:
            # Convert string to UUID for proper database comparison
            ticket_uuid = UUID(str(support_ticket_id))
            return db.query(SupportTicket).filter(
                SupportTicket.id == ticket_uuid
            ).first()
        except Exception as e:
            # If the string is not a valid UUID, return None
            logger.log_database_operation(
                operation="get_support_ticket_by_id",
                table="support_tickets",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e
    
    @staticmethod
    def get_support_tickets(
        db: Session,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SupportTicket]:
        """Get support tickets with optional filtering."""
        try:
            query = db.query(SupportTicket)
            
            if category:
                query = query.filter(SupportTicket.category == category)
            
            if priority:
                query = query.filter(SupportTicket.priority == priority)
            
            return query.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit).all()
        except Exception as e:
            logger.log_database_operation(
                operation="get_support_tickets",
                table="support_tickets",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e
    
    @staticmethod
    def count_support_tickets(
        db: Session,
        category: Optional[str] = None,
        priority: Optional[str] = None
    ) -> int:
        """Count support tickets with optional filtering."""
        try:
            query = db.query(SupportTicket)
            
            if category:
                query = query.filter(SupportTicket.category == category)
            
            if priority:
                query = query.filter(SupportTicket.priority == priority)
            
            return query.count()
        except Exception as e:
            logger.log_database_operation(
                operation="count_support_tickets",
                table="support_tickets",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e
