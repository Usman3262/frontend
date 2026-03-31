"""
Story routes.

Thin HTTP layer - delegates business logic to StoryService.
"""

from typing import Optional
import logging
import time
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    StoryCreateRequest,
    StoryResponse,
    UserAuthRequest,
    PostStoryRequest,
    PostStoryResponse,
    StoryListResponse,
    StoryListItemResponse,
    DeleteStoryResponse,
)
from app.services.story_service import StoryService
from app.services.search_service import SearchService

router = APIRouter(prefix="/stories", tags=["stories"])
logger = logging.getLogger(__name__)

@router.post("/post-story", response_model=PostStoryResponse, status_code=201)
async def post_story(
    story: PostStoryRequest,
    db: AsyncSession = Depends(get_db),
) -> PostStoryResponse:
    """
    Post a new story with optional user authentication.
    
    If anonymous_number is provided, uses existing user (requires password).
    If anonymous_number is not provided, creates a new anonymous user.
    
    AI moderation is automatically queued as a background task.
    
    Args:
        story: Story data (content, category, optional auth)
        db: Database session
    
    Returns:
        PostStoryResponse with story_id, anonymous_number, success status
    
    Raises:
        HTTPException: If validation fails or auth is invalid
    """
    start_time = time.time()
    logger.info(f"⏱️  POST /post-story started")
    
    try:
        logger.info(f"⏱️  Calling StoryService.post_story...")
        service_start = time.time()
        result = await StoryService.post_story(story, db)
        service_time = time.time() - service_start
        logger.info(f"⏱️  StoryService.post_story completed in {service_time:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"✅ POST /post-story completed in {total_time:.2f}s - Story ID: {result.story_id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        total_time = time.time() - start_time
        logger.error(f"❌ POST /post-story failed after {total_time:.2f}s: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to post story: {str(e)}")

@router.post("", response_model=StoryResponse, status_code=201)
async def create_story(
    story: StoryCreateRequest,
    anon_num: str = Query(...),
    password: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Create a new story."""
    return await StoryService.create_story(story, anon_num, password, db)

@router.get("", response_model=StoryListResponse)
async def get_stories(
    category: Optional[str] = Query(None, description="Filter by category"),
    search_text: Optional[str] = Query(None, description="Full-text search query"),
    sort_by: str = Query("new", description="Sort order: new, top, trending"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
) -> StoryListResponse:
    """
    Get paginated story list with optional search and filtering.
    
    Query Parameters:
    - category: Filter by category (e.g., "Life Lessons")
    - search_text: Full-text search using Meilisearch
    - sort_by: new (default), top (by views), trending (recent+popular)
    - limit: 1-100 results per page (default: 20)
    - offset: Pagination offset (default: 0)
    
    Returns:
    - List of stories with snippets, reactions, categories, etc.
    - Total count and pagination info
    """
    try:
        if search_text:
            # Use SearchService for full-text search
            return await SearchService.search_stories_with_filters(
                search_text, category, sort_by, limit, offset, db
            )
        else:
            # Use StoryService for feed with filtering
            return await StoryService.get_story_feed(
                category, sort_by, limit, offset, db
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stories: {str(e)}")

@router.get("/{story_id}", response_model=dict)
async def get_story(
    story_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get full story details by ID.
    
    Path Parameters:
    - story_id: Unique story identifier
    
    Returns:
    - Full story content with reactions, summary, lessons, metadata
    - Increments view count on successful retrieval
    """
    try:
        return await StoryService.get_story(story_id, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get story: {str(e)}")

@router.delete("/{story_id}", response_model=DeleteStoryResponse)
async def delete_story(
    story_id: int,
    anonymous_number: str = Query(..., alias="anon_num", description="User's anonymous number"),
    password: str = Query(..., description="User's password"),
    db: AsyncSession = Depends(get_db),
) -> DeleteStoryResponse:
    """
    Delete a story (author only).
    
    Path Parameters:
    - story_id: Unique story identifier
    
    Query Parameters:
    - anonymous_number (anon_num): User's anonymous number (e.g., "#4821")
    - password: User's password for authentication
    
    Returns:
    - DeleteStoryResponse with success status and message
    
    Raises:
    - 404: Story not found
    - 401: Invalid credentials
    - 403: User is not the story author
    - 500: Server error
    """
    try:
        result = await StoryService.delete_story(story_id, anonymous_number, password, db)
        return DeleteStoryResponse(
            success=True,
            message=result["message"],
            id=result["id"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete story: {str(e)}")
