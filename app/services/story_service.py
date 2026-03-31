"""
Story service layer.

Handles all story CRUD operations and business logic.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from fastapi import HTTPException

from app.models import Story, AnonymousUser, Reaction
from app.schemas import (
    StoryCreateRequest,
    StoryResponse,
    StoryFeedResponse,
    PostStoryRequest,
    PostStoryResponse,
    StoryListResponse,
    StoryListItemResponse,
)
from app.utils.validators import validate_story_content, validate_category
from app.utils.constants import ERROR_STORY_NOT_FOUND, ERROR_USER_NOT_FOUND
from app.services.auth_service import AuthService
from app.utils.ai import summarize_story, moderate_content
from app.tasks import process_story_event

logger = logging.getLogger(__name__)

class StoryService:
    """Service for story operations."""
    
    @staticmethod
    async def create_story(
        story_data: StoryCreateRequest,
        anonymous_number: str,
        password: str,
        db: AsyncSession,
    ) -> StoryResponse:
        """
        Create a new story.
        
        Args:
            story_data: Story creation request data
            anonymous_number: User's anonymous number
            password: User's password
            db: Database session
        
        Returns:
            Created story as StoryResponse
        
        Raises:
            HTTPException: If validation or auth fails
        """
        # Validate content
        is_valid, error = validate_story_content(story_data.content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Validate category
        if story_data.category:
            is_valid, error = validate_category(story_data.category)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        
        # Authenticate user
        user = await AuthService.get_user_by_number(anonymous_number, db)
        if not user:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        
        if not AuthService.verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account inactive")
        
        # Check content safety (AI moderation)
        is_safe, reason = await moderate_content(story_data.content)
        
        # Create story
        story = Story(
            author_id=user.id,
            content=story_data.content.strip(),
            category=story_data.category,
            image_url=story_data.image_url,
            is_published=is_safe,  # Auto-publish if safe
            moderation_status="approved" if is_safe else "pending",
        )
        
        db.add(story)
        await db.commit()
        await db.refresh(story)
        
        logger.info(f"Story created: id={story.id}, author={anonymous_number}")
        
        return StoryResponse.from_orm(story)
    
    @staticmethod
    async def post_story(
        story_data: PostStoryRequest,
        db: AsyncSession,
    ) -> PostStoryResponse:
        """
        Post a new story with optional user authentication.
        
        If anonymous_number is not provided, creates a new anonymous user.
        If anonymous_number is provided, validates password.
        
        Args:
            story_data: Story data with optional user credentials
            db: Database session
        
        Returns:
            PostStoryResponse with story_id, anonymous_number, success
        
        Raises:
            HTTPException: If validation or auth fails
        """
        # Validate content
        is_valid, error = validate_story_content(story_data.content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Validate category if provided
        if story_data.category:
            is_valid, error = validate_category(story_data.category)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
        
        # Handle user authentication or creation
        if story_data.anonymous_number:
            # Use existing user - validate password required
            if not story_data.password:
                raise HTTPException(
                    status_code=400,
                    detail="Password required when using existing anonymous number"
                )
            
            # Authenticate user
            user = await AuthService.get_user_by_number(
                story_data.anonymous_number, db
            )
            if not user:
                raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
            
            if not AuthService.verify_password(story_data.password, user.password_hash):
                raise HTTPException(status_code=401, detail="Invalid password")
            
            if not user.is_active:
                raise HTTPException(status_code=403, detail="User account inactive")
            
            generated_password = None  # Existing user, no new password to return
        else:
            # Create new user with random password
            generated_password = AuthService.generate_random_password()
            hashed_password = AuthService.hash_password(generated_password)
            
            user = AnonymousUser(
                anonymous_number=AuthService.generate_anonymous_number(),
                password_hash=hashed_password,
                is_active=True,
            )
            db.add(user)
            await db.flush()  # Get the ID without hitting DB again
        
        # Create story - auto-publish for development (no moderation queue)
        story = Story(
            author_id=user.id,
            content=story_data.content.strip(),
            category=story_data.category,
            image_url=story_data.image_url,
            is_published=True,  # Auto-publish for development
            moderation_status="approved",  # Skip moderation during dev
        )
        
        db.add(story)
        await db.flush()  # Get story ID
        
        logger.info(
            f"Story posted: id={story.id}, author={user.anonymous_number}, "
            f"new_user={story_data.anonymous_number is None}"
        )
        
        # Commit all changes together (one network round-trip)
        await db.commit()
        
        # Send story event to Celery worker (fire-and-forget)
        try:
            process_story_event.delay(story.id, "published")
            logger.info(f"📤 Story {story.id} event sent to Celery worker")
        except Exception as e:
            logger.warning(f"Could not queue story event to Celery: {e}")
        
        return PostStoryResponse(
            success=True,
            message="Story posted successfully",
            story_id=story.id,
            anonymous_number=user.anonymous_number,
            password=generated_password,  # Only for new users
        )
    
    @staticmethod
    async def get_story_feed(
        category: str | None,
        sort_by: str,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> StoryListResponse:
        """
        Get paginated story feed with optional filtering and sorting.
        
        Args:
            category: Filter by category (optional)
            sort_by: Sort order ('new', 'top', 'trending')
            limit: Results limit (1-100)
            offset: Pagination offset
            db: Database session
        
        Returns:
            StoryListResponse with paginated stories, total count, and pagination info
        """
        # Build base query - only published stories
        query = select(Story).where(Story.is_published == True)
        
        # Apply category filter
        if category:
            is_valid, error = validate_category(category)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            query = query.where(Story.category == category)
        
        # Get total count before pagination
        count_result = await db.execute(
            select(func.count(Story.id)).where(Story.is_published == True)
        )
        total = count_result.scalar() or 0
        
        if category:
            count_query = select(func.count(Story.id)).where(
                (Story.is_published == True) & (Story.category == category)
            )
            count_result = await db.execute(count_query)
            total = count_result.scalar() or 0
        
        # Apply sorting
        if sort_by == "top":
            query = query.order_by(desc(Story.view_count))
        elif sort_by == "trending":
            query = query.order_by(desc(Story.updated_at), desc(Story.view_count))
        else:  # "new"
            query = query.order_by(desc(Story.created_at))
        
        # Pagination
        query = query.offset(offset).limit(limit)
        result = await db.execute(query)
        stories = result.scalars().all()
        
        # Build response items
        story_items = []
        for story in stories:
            # Get reaction count
            reaction_count_result = await db.execute(
                select(func.count(Reaction.id)).where(Reaction.story_id == story.id)
            )
            reactions_count = reaction_count_result.scalar() or 0
            
            # Create snippet (first 150 chars)
            snippet = story.content[:150]
            if len(story.content) > 150:
                snippet += "..."
            
            item = StoryListItemResponse(
                id=story.id,
                snippet=snippet,
                category=story.category,
                media_url=story.image_url,
                reactions_count=reactions_count,
                summary=story.summary,
                lessons=story.lessons,
                created_at=story.created_at,
                view_count=story.view_count,
            )
            story_items.append(item)
        
        return StoryListResponse(
            total=total,
            limit=limit,
            offset=offset,
            stories=story_items,
        )
    
    @staticmethod
    async def get_story(
        story_id: int,
        db: AsyncSession,
    ) -> dict:
        """
        Get full story details with reactions breakdown.
        
        Increments view count on retrieval.
        Fetches story content, summary, lessons, reactions, and metadata.
        
        Args:
            story_id: Story ID
            db: Database session
        
        Returns:
            Dict with full story details including:
            - id, content, category, media_url
            - summary, lessons, created_at, view_count
            - reactions with type breakdown and counts
        
        Raises:
            HTTPException: If story not found or not published
        """
        # Fetch story
        result = await db.execute(
            select(Story).where(
                (Story.id == story_id) & (Story.is_published == True)
            )
        )
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Increment view count
        story.view_count += 1
        await db.commit()
        
        # Get reaction counts by type
        reaction_types = ["Relatable", "Inspired", "StayStrong", "Helpful"]
        reactions = {}
        total_reactions = 0
        
        for reaction_type in reaction_types:
            count_result = await db.execute(
                select(func.count(Reaction.id)).where(
                    (Reaction.story_id == story_id) & 
                    (Reaction.reaction_type == reaction_type)
                )
            )
            count = count_result.scalar() or 0
            reactions[reaction_type] = count
            total_reactions += count
        
        return {
            "id": story.id,
            "content": story.content,
            "category": story.category,
            "media_url": story.image_url,
            "summary": story.summary,
            "lessons": story.lessons,
            "created_at": story.created_at,
            "updated_at": story.updated_at,
            "view_count": story.view_count,
            "is_published": story.is_published,
            "moderation_status": story.moderation_status,
            "reactions": {
                "counts": reactions,
                "total": total_reactions,
                "breakdown": {
                    reaction_type: round((count / total_reactions * 100), 1) 
                    if total_reactions > 0 else 0
                    for reaction_type, count in reactions.items()
                },
            },
        }
    
    @staticmethod
    async def get_story_detail(
        story_id: int,
        db: AsyncSession,
    ) -> StoryResponse:
        """
        Get full story details and increment view count.
        
        Args:
            story_id: Story ID
            db: Database session
        
        Returns:
            Story details as StoryResponse
        
        Raises:
            HTTPException: If story not found
        """
        result = await db.execute(
            select(Story).where(
                (Story.id == story_id) & (Story.is_published == True)
            )
        )
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Increment view count
        story.view_count += 1
        await db.commit()
        
        return StoryResponse.from_orm(story)
    
    @staticmethod
    async def delete_story(
        story_id: int,
        anonymous_number: str,
        password: str,
        db: AsyncSession,
    ) -> dict:
        """
        Delete a story (author only).
        
        Args:
            story_id: Story to delete
            anonymous_number: User's anonymous number
            password: User's password
            db: Database session
        
        Returns:
            Success message dict
        
        Raises:
            HTTPException: If not found or unauthorized
        """
        # Get story
        result = await db.execute(select(Story).where(Story.id == story_id))
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Authenticate user and verify ownership
        user = await AuthService.get_user_by_number(anonymous_number, db)
        if not user or not AuthService.verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if story.author_id != user.id:
            raise HTTPException(status_code=403, detail="Can only delete own stories")
        
        await db.delete(story)
        await db.commit()
        
        logger.info(f"Story deleted: id={story_id}, author={anonymous_number}")
        
        return {"message": "Story deleted successfully", "id": story_id}
