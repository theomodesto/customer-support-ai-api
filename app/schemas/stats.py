from pydantic import BaseModel


class StatsResponse(BaseModel):
    """Schema for statistics response."""
    total_support_tickets: int
    category_counts: dict
    priority_counts: dict
    avg_confidence: float = 0.0
    last_7_days: dict