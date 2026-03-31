"""
Pydantic schemas for request/response validation and serialization.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class UserSignupRequest(BaseModel):
    """Request schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v

class UserAuthRequest(BaseModel):
    """Request schema for user authentication."""
    anonymous_number: str
    password: str

class UserResponse(BaseModel):
    """Response schema for user information."""
    id: int
    anonymous_number: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class StoryCreateRequest(BaseModel):
    """Request schema for creating a story."""
    content: str = Field(..., min_length=10, max_length=2000)
    category: Optional[str] = None
    image_url: Optional[str] = None
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Story content cannot be empty")
        return v.strip()

class StoryResponse(BaseModel):
    """Response schema for story details."""
    id: int
    author_id: int
    content: str
    category: Optional[str]
    image_url: Optional[str]
    summary: Optional[str]
    is_published: bool
    moderation_status: str
    created_at: datetime
    updated_at: datetime
    view_count: int
    
    class Config:
        from_attributes = True

class StoryFeedResponse(BaseModel):
    """Response schema for story in feed."""
    id: int
    content: str
    category: Optional[str]
    summary: Optional[str]
    created_at: datetime
    view_count: int
    reactions_count: int = 0
    
    class Config:
        from_attributes = True

class ReactionCreateRequest(BaseModel):
    """Request schema for creating a reaction (anonymous)."""
    story_id: int
    reaction_type: str
    
    @field_validator("reaction_type")
    @classmethod
    def validate_reaction(cls, v: str) -> str:
        """Validate reaction type."""
        valid = {"Relatable", "Inspired", "StayStrong", "Helpful"}
        if v not in valid:
            raise ValueError(f"Invalid reaction type. Must be one of: {valid}")
        return v

class ReactRequest(BaseModel):
    """Request schema for adding a reaction with authentication."""
    story_id: int
    reaction_type: str
    anonymous_number: str
    password: str
    
    @field_validator("reaction_type")
    @classmethod
    def validate_reaction(cls, v: str) -> str:
        """Validate reaction type."""
        valid = {"Relatable", "Inspired", "StayStrong", "Helpful"}
        if v not in valid:
            raise ValueError(f"Invalid reaction type. Must be one of: {valid}")
        return v

class ReactResponse(BaseModel):
    """Response schema for adding a reaction."""
    user_id: int
    story_id: int
    reaction_type: str
    total_reactions: int

class ReactionResponse(BaseModel):
    """Response schema for reaction."""
    id: int
    story_id: int
    reaction_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ReactionCountResponse(BaseModel):
    """Reaction counts for a story."""
    story_id: int
    relatable: int = 0
    inspired: int = 0
    stay_strong: int = 0
    helpful: int = 0
    total: int = 0

class SearchRequest(BaseModel):
    """Request schema for search."""
    query: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class SearchResult(BaseModel):
    """Search result item."""
    id: int
    content: str
    category: Optional[str]
    created_at: datetime
    view_count: int
    
    class Config:
        from_attributes = True

class SearchResponse(BaseModel):
    """Response schema for search results."""
    query: str
    total: int
    results: list[SearchResult]
    limit: int
    offset: int

class PostStoryRequest(BaseModel):
    """Request schema for posting a story (with optional auth)."""
    content: str = Field(..., min_length=10, max_length=2000)
    category: Optional[str] = None
    image_url: Optional[str] = None
    anonymous_number: Optional[str] = None  # If provided, uses existing user
    password: Optional[str] = None  # Required if anonymous_number provided
    
    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Story content cannot be empty")
        return v.strip()

class PostStoryResponse(BaseModel):
    """Response schema for posting a story."""
    success: bool
    message: str
    story_id: int
    anonymous_number: str
    password: Optional[str] = None  # Only included for new users

class StoryListItemResponse(BaseModel):
    """Response schema for story in list/feed."""
    id: int
    snippet: str  # First 150 chars of content
    category: Optional[str]
    media_url: Optional[str]  # Alias for image_url
    reactions_count: int = 0
    summary: Optional[str]
    lessons: Optional[str]  # AI-extracted key lessons
    created_at: datetime
    view_count: int
    
    class Config:
        from_attributes = True

class StoryListResponse(BaseModel):
    """Response schema for paginated story list."""
    total: int
    limit: int
    offset: int
    stories: list[StoryListItemResponse]

class DeleteStoryResponse(BaseModel):
    """Response schema for story deletion."""
    success: bool
    message: str
    id: int

class FCMTokenRequest(BaseModel):
    """Request schema for FCM token registration."""
    fcm_token: str

class NotificationPreferences(BaseModel):
    """Notification preference settings."""
    enable_daily_digest: bool = False
    enable_top_story: bool = False

class TopStoryDigestResponse(BaseModel):
    """Response for top story of the day."""
    id: int
    title: str
    snippet: str
    category: Optional[str]
    views: int
    summary: Optional[str]
    lessons: Optional[str]

class DailyDigestResponse(BaseModel):
    """Response for daily digest."""
    title: str
    stories: list[dict]
    count: int
