from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.db.database import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from app.utils.logger import logger

from app.schemas.support_tickets import SupportTicketRequestCreate, SupportTicketResponse, SupportTicketList
from app.schemas.enums import CategoryEnum
from app.schemas.errors import ErrorResponse
from app.repository.support_ticket_repo import SupportTicketRepo
from app.repository.support_ticket_ai_classification_repo import SupportTicketAIClassificationRepo

router = APIRouter(prefix="/requests", tags=["Requests"])


@router.post(
    "", 
    response_model=SupportTicketResponse,
    status_code=201,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def create_support_request(
    request: SupportTicketRequestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new support request with AI classification.
    
    Accepts either:
    - `{"text": "customer message"}` 
    - `{"subject": "Issue title", "body": "detailed description"}`
    
    Stores the raw data and triggers AI processing to classify the request
    into categories (technical, billing, general) with confidence_score scores and summaries.
    """
    try:
        request_data = SupportTicketRequestCreate(
            subject=request.subject,
            body=request.body,
            language=request.language,
        )
        # Use AI classification repo to create ticket with AI processing
        support_ticket = SupportTicketRepo.create_support_ticket(db, request_data)
        
        # Add AI classification as a background task
        background_tasks.add_task(
            SupportTicketAIClassificationRepo.classify_ticket_and_update,
            ticket_id=UUID(str(support_ticket.id))
        )
        return support_ticket
    except Exception as e:
        logger.log_api_error(
            method="POST",
            path="/requests",
            status_code=500,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create support request: {str(e)}"
        )


@router.get(
    "/{support_ticket_id}",
    response_model=SupportTicketResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Ticket not found"},
        422: {"model": ErrorResponse, "description": "Invalid ticket ID"}
    }
)
def get_support_request(
    support_ticket_id: UUID = Path(..., description="Support ticket UUID"),
    db: Session = Depends(get_db)
):
    """
    Get a specific support request by ID including AI classification results.
    """
    try:
        ticket = SupportTicketRepo.get_support_ticket_by_id(db, str(support_ticket_id))
        if not ticket:
            logger.log_api_error(
                method="GET",
                path=f"/requests/{support_ticket_id}",
                status_code=404,
                error="Support request not found"
            )
            raise HTTPException(
                status_code=404,
                detail="Support request not found"
            )
        return ticket
    except HTTPException:
        raise
    except Exception as e:
        logger.log_api_error(
            method="GET",
            path=f"/requests/{support_ticket_id}",
            status_code=500,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve support request: {str(e)}"
        )


@router.get(
    "",
    response_model=SupportTicketList,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"}
    }
)
def list_support_requests(
    category: Optional[CategoryEnum] = Query(
        None, 
        description="Filter by category (technical, billing, general)"
    ),
    priority: Optional[str] = Query(
        None, 
        description="Filter by priority (low, medium, high)"
    ),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(20, ge=1, le=100, description="Number of items per page"),
    db: Session = Depends(get_db)
):
    """
    List support requests with optional filtering by category and priority.
    
    Supports pagination and filtering:
    - `category`: Filter by AI-classified category (technical, billing, general)
    - `priority`: Filter by priority level (low, medium, high)
    - `page`: Page number for pagination (default: 1)
    - `size`: Items per page (default: 20, max: 100)
    """
    try:
        skip = (page - 1) * size
        
        # Get tickets with filtering
        support_tickets_db = SupportTicketRepo.get_support_tickets(
            db=db,
            category=category.value if category else None,
            priority=priority,
            skip=skip,
            limit=size
        )
        
        # Get total count for pagination
        total = SupportTicketRepo.count_support_tickets(
            db=db,
            category=category.value if category else None,
            priority=priority
        )
        
        has_next = (skip + size) < total
        
        return SupportTicketList(
            support_tickets=[SupportTicketResponse.model_validate(support_ticket) for support_ticket in support_tickets_db],
            total=total,
            page=page,
            size=size,
            has_next=has_next
        )
    
    except Exception as e:
        logger.log_api_error(
            method="GET",
            path="/requests",
            status_code=400,
            error=str(e)
        )
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retrieve support requests: {str(e)}"
        ) 