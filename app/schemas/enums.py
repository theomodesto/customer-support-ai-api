from enum import Enum

class CategoryEnum(str, Enum):
    """Valid support ticket categories."""
    technical = "technical"
    billing = "billing"
    general = "general"

class Priority(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"            # maps “Critical” in raw data → HIGH

class Category(str, Enum):
    TECHNICAL = "technical"
    BILLING   = "billing"
    GENERAL   = "general"

class Confidence(str, Enum):
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"