"""
Reaction service layer.

Handles all reaction operations and business logic.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models import Reaction, Story
from app.schemas import ReactionCreateRequest, ReactionCountResponse, ReactRequest, ReactResponse, UserAuthRequest
from app.services.auth_service import AuthService
from app.utils.validators import validate_reaction
from app.utils.constants import ERROR_STORY_NOT_FOUND

logger = logging.getLogger(__name__)

class ReactionService:
    """Service for reaction operations."""
    
    @staticmethod
    async def add_reaction(
        reaction_data: ReactionCreateRequest,
        db: AsyncSession,
    ) -> dict:
        """
        Add a reaction to a story (anonymous allowed).
        
        Args:
            reaction_data: Reaction creation data
            db: Database session
        
        Returns:
            Reaction confirmation dictionary
        
        Raises:
            HTTPException: If validation fails or story not found
        """
        # Validate reaction type
        is_valid, error = validate_reaction(reaction_data.reaction_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Verify story exists and is published
        result = await db.execute(
            select(Story).where(
                (Story.id == reaction_data.story_id) & (Story.is_published == True)
            )
        )
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Create reaction (anonymous)
        reaction = Reaction(
            story_id=reaction_data.story_id,
            reaction_type=reaction_data.reaction_type,
            user_id=None,  # Anonymous reaction
        )
        
        db.add(reaction)
        await db.commit()
        
        # Get updated count
        count_result = await db.execute(
            select(func.count(Reaction.id)).where(Reaction.story_id == reaction_data.story_id)
        )
        total = count_result.scalar() or 0
        
        logger.info(f"Reaction added: story={reaction_data.story_id}, type={reaction_data.reaction_type}")
        
        return {
            "message": "Reaction added successfully",
            "story_id": reaction_data.story_id,
            "reaction_type": reaction_data.reaction_type,
            "total_reactions": total,
        }
    
    @staticmethod
    async def add_authenticated_reaction(
        react_data: ReactRequest,
        db: AsyncSession,
    ) -> ReactResponse:
        """
        Add a reaction with user authentication validation.
        
        Args:
            react_data: Reaction data with credentials
            db: Database session
        
        Returns:
            ReactResponse with user_id, story_id, reaction_type, total_reactions
        
        Raises:
            HTTPException: If authentication fails, validation fails, or story not found
        """
        # Validate user credentials via AuthService
        auth_data = UserAuthRequest(
            anonymous_number=react_data.anonymous_number,
            password=react_data.password,
        )
        user = await AuthService.authenticate(auth_data, db)
        
        # Validate reaction type
        is_valid, error = validate_reaction(react_data.reaction_type)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Verify story exists and is published
        result = await db.execute(
            select(Story).where(
                (Story.id == react_data.story_id) & (Story.is_published == True)
            )
        )
        story = result.scalar_one_or_none()
        
        if not story:
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Create reaction with authenticated user
        reaction = Reaction(
            story_id=react_data.story_id,
            reaction_type=react_data.reaction_type,
            user_id=user.id,
        )
        
        db.add(reaction)
        await db.commit()
        
        # Get updated total reaction count for this story
        count_result = await db.execute(
            select(func.count(Reaction.id)).where(Reaction.story_id == react_data.story_id)
        )
        total_reactions = count_result.scalar() or 0
        
        logger.info(f"Authenticated reaction added: user={user.id}, story={react_data.story_id}, type={react_data.reaction_type}")
        
        return ReactResponse(
            user_id=user.id,
            story_id=react_data.story_id,
            reaction_type=react_data.reaction_type,
            total_reactions=total_reactions,
        )
    
    @staticmethod
    async def get_reaction_counts(
        story_id: int,
        db: AsyncSession,
    ) -> ReactionCountResponse:
        """
        Get reaction counts for a story.
        
        Args:
            story_id: Story ID
            db: Database session
        
        Returns:
            Reaction counts by type
        
        Raises:
            HTTPException: If story not found
        """
        # Verify story exists
        result = await db.execute(select(Story).where(Story.id == story_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Count each reaction type
        reaction_counts = {
            "Relatable": 0,
            "Inspired": 0,
            "StayStrong": 0,
            "Helpful": 0,
        }
        
        for reaction_type in reaction_counts.keys():
            count_result = await db.execute(
                select(func.count(Reaction.id)).where(
                    (Reaction.story_id == story_id) & 
                    (Reaction.reaction_type == reaction_type)
                )
            )
            reaction_counts[reaction_type] = count_result.scalar() or 0
        
        total = sum(reaction_counts.values())
        
        return ReactionCountResponse(
            story_id=story_id,
            relatable=reaction_counts["Relatable"],
            inspired=reaction_counts["Inspired"],
            stay_strong=reaction_counts["StayStrong"],
            helpful=reaction_counts["Helpful"],
            total=total,
        )
    
    @staticmethod
    async def get_reaction_breakdown(
        story_id: int,
        db: AsyncSession,
    ) -> dict:
        """
        Get reaction breakdown with percentages.
        
        Args:
            story_id: Story ID
            db: Database session
        
        Returns:
            Breakdown dictionary with counts and percentages
        
        Raises:
            HTTPException: If story not found
        """
        # Verify story exists
        result = await db.execute(select(Story).where(Story.id == story_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=ERROR_STORY_NOT_FOUND)
        
        # Get all reactions
        reactions_result = await db.execute(
            select(Reaction).where(Reaction.story_id == story_id)
        )
        reactions = reactions_result.scalars().all()
        
        # Count by type
        counts = {
            "Relatable": 0,
            "Inspired": 0,
            "StayStrong": 0,
            "Helpful": 0,
        }
        
        for reaction in reactions:
            if reaction.reaction_type in counts:
                counts[reaction.reaction_type] += 1
        
        total = len(reactions)
        
        # Calculate percentages
        percentages = {}
        for reaction_type, count in counts.items():
            if total > 0:
                percentages[reaction_type] = round((count / total * 100), 2)
            else:
                percentages[reaction_type] = 0.0
        
        return {
            "story_id": story_id,
            "total_reactions": total,
            "counts": counts,
            "percentages": percentages,
        }
