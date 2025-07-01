from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    error_code: Optional[str] = None 