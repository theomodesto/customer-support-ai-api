from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.stats import StatsResponse
from app.schemas.errors import ErrorResponse
from app.repository.stats_repo import StatsRepo
from app.utils.logger import logger

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get(
    "",
    response_model=StatsResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Failed to retrieve statistics"}
    }
)
def get_statistics(
    days: int = Query(
        7, 
        ge=1, 
        le=365, 
        description="Number of days to include in statistics (default: 7)"
    ),
    db: Session = Depends(get_db)
):
    """
    Get support request statistics for the specified time period.
    
    Returns:
    - Total number of support integer tickets
    - Counts by category (technical, billing, general)
    - Counts by priority (low, medium, high)
    - Average confidence_score score of AI classifications
    - Daily breakdown for the specified period
    
    Parameters:
    - `days`: Number of days to include (default: 7, max: 365)
    """
    try:
        stats = StatsRepo.get_stats(db, days=days)
        return StatsResponse(**stats)
    except Exception as e:
        logger.log_api_error(
            method="GET",
            path="/stats",
            status_code=500,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        ) 