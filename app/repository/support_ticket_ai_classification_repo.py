from app.repository.support_ticket_repo import SupportTicketRepo
from app.repository.ai_classification_results_repo import AIClassificationResultRepo
from uuid import UUID
from app.db.database import SessionLocal
from app.utils.logger import logger

class SupportTicketAIClassificationRepo:
    """Service for database operations on ticket with AI."""    

    @staticmethod
    async def classify_ticket_and_update(ticket_id: UUID):
        """Fetch ticket and classify it."""
        db = SessionLocal()
        try:
            ticket = SupportTicketRepo.get_support_ticket_by_id(db, str(ticket_id))
            if ticket:
                await AIClassificationResultRepo.create_ai_classification_and_update_ticket(db, ticket)
        except Exception as e:
            logger.log_database_operation(
                operation="classify_ticket_and_update",
                table="support_tickets",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
        finally:
            db.close()
