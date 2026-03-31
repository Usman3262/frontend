"""Input validation utilities."""

from typing import Optional
from app.utils.constants import VALID_CATEGORIES, VALID_REACTIONS
from app.config import get_settings

settings = get_settings()

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, ""

def validate_story_content(content: str) -> tuple[bool, str]:
    """
    Validate story content length.
    
    Args:
        content: Content to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    content = content.strip()
    if len(content) < settings.min_story_length:
        return False, f"Story must be at least {settings.min_story_length} characters"
    if len(content) > settings.max_story_length:
        return False, f"Story must be at most {settings.max_story_length} characters"
    return True, ""

def validate_category(category: Optional[str]) -> tuple[bool, str]:
    """
    Validate story category.
    
    Args:
        category: Category to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if category and category not in VALID_CATEGORIES:
        return False, f"Invalid category. Valid options: {', '.join(VALID_CATEGORIES)}"
    return True, ""

def validate_reaction(reaction_type: str) -> tuple[bool, str]:
    """
    Validate reaction type.
    
    Args:
        reaction_type: Reaction to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if reaction_type not in VALID_REACTIONS:
        return False, f"Invalid reaction. Valid options: {', '.join(VALID_REACTIONS)}"
    return True, ""
