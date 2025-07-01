from sqlalchemy.orm import Session
from app.models.support_ticket import SupportTicket
from app.models.ai_classifications import AIClassificationResult
from app.services.ai_classifier import ai_classifier
from app.utils.logger import logger


class AIClassificationResultRepo:
    """Service for database operations on AI classifications."""

    @staticmethod
    async def create_ai_classification(
        db: Session,
        supportTicket: SupportTicket
    ) -> AIClassificationResult:
        """Create AI classification for a support ticket."""
        # Classify the ticket
        try:
            classification_result = await ai_classifier.classify_and_summarize(
                body=str(supportTicket.body),
                subject=str(supportTicket.subject)
            )

            if classification_result.summary:
                supportTicket.summary = classification_result.summary  # type: ignore
            
            # Create classification record
            ai_classification = AIClassificationResult(
                support_ticket_id=supportTicket.id,
                **classification_result.model_dump()
            )
            
            db.add(ai_classification)
            db.add(supportTicket)
            db.commit()
            db.refresh(ai_classification)
            return ai_classification
        except Exception as e:
            db.rollback()
            logger.log_database_operation(
                operation="create",
                table="ai_classification_results",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e

    @staticmethod
    async def create_ai_classification_and_update_ticket(
        db: Session,
        supportTicket: SupportTicket
    ) -> AIClassificationResult:
        """Create AI classification for a support ticket."""
        # Classify the ticket
        try:
            classification_result = await ai_classifier.classify_and_summarize(
                body=str(supportTicket.body),
                subject=str(supportTicket.subject)
            )

            if classification_result.category:
                supportTicket.category = classification_result.category  # type: ignore
            
            if classification_result.confidence_score:
                supportTicket.confidence_score = classification_result.confidence_score  # type: ignore
                
            if classification_result.summary:
                supportTicket.summary = classification_result.summary  # type: ignore

            if classification_result.priority:
                supportTicket.priority = classification_result.priority  # type: ignore
            
            # Create classification record
            ai_classification = AIClassificationResult(
                support_ticket_id=supportTicket.id,
                **classification_result.model_dump()
            )
            
            db.add(ai_classification)
            db.add(supportTicket)
            db.commit()
            db.refresh(ai_classification)
            return ai_classification
        except Exception as e:
            db.rollback()
            logger.log_database_operation(
                operation="create",
                table="ai_classification_results",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e
