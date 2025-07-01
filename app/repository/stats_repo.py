from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any
from datetime import datetime, timedelta
from app.models.support_ticket import SupportTicket
from app.models.ai_classifications import AIClassificationResult
from app.utils.logger import logger


class StatsRepo:
    """Service for database operations on stats."""
    
    @staticmethod
    def get_stats(db: Session, days: int = 7) -> Dict[str, Any]:
        """Get statistics for the past N days."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Total support tickets
            total_support_tickets = db.query(SupportTicket).filter(
                SupportTicket.created_at >= cutoff_date
            ).count()
            
            # Category counts
            category_counts = db.query(
                AIClassificationResult.category,
                func.count(AIClassificationResult.id)
            ).join(SupportTicket).filter(
                SupportTicket.created_at >= cutoff_date
            ).group_by(AIClassificationResult.category).all()
            
            category_dict = {category: count for category, count in category_counts}
            
            # Priority counts
            priority_counts = db.query(
                SupportTicket.priority,
                func.count(SupportTicket.id)
            ).filter(
                SupportTicket.created_at >= cutoff_date,
                SupportTicket.priority.isnot(None)
            ).group_by(SupportTicket.priority).all()
            
            priority_dict = {priority: count for priority, count in priority_counts}
            
            # Average confidence_score
            avg_confidence_result = db.query(
                func.avg(AIClassificationResult.confidence_score)
            ).join(SupportTicket).filter(
                SupportTicket.created_at >= cutoff_date
            ).scalar()
            
            avg_confidence = float(avg_confidence_result) if avg_confidence_result else 0.0
            
            # Daily breakdown
            daily_counts = db.query(
                func.date(SupportTicket.created_at).label('date'),
                func.count(SupportTicket.id).label('count')
            ).filter(
                SupportTicket.created_at >= cutoff_date
            ).group_by(func.date(SupportTicket.created_at)).all()
            
            daily_dict = {str(date): count for date, count in daily_counts}
            
            return {
                "total_support_tickets": total_support_tickets,
                "category_counts": category_dict,
                "priority_counts": priority_dict,
                "avg_confidence": round(avg_confidence, 3),
                "last_7_days": daily_dict
            }
        except Exception as e:
            logger.log_database_operation(
                operation="get_stats",
                table="stats",
                processing_time_ms=0,
                success=False,
                error=str(e)
            )
            raise e