"""
Reaction routes.

Thin HTTP layer - delegates business logic to ReactionService.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ReactionCreateRequest, ReactionCountResponse, ReactRequest, ReactResponse
from app.services.reaction_service import ReactionService

router = APIRouter(prefix="/reactions", tags=["reactions"])

@router.post("", status_code=201)
async def add_reaction(
    reaction: ReactionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add reaction to a story."""
    return await ReactionService.add_reaction(reaction, db)

@router.post("/react", status_code=201, response_model=ReactResponse)
async def add_authenticated_reaction(
    react: ReactRequest,
    db: AsyncSession = Depends(get_db),
):
    """Add reaction with user authentication."""
    return await ReactionService.add_authenticated_reaction(react, db)

@router.get("/{story_id}", response_model=ReactionCountResponse)
async def get_reactions(
    story_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get reaction counts."""
    return await ReactionService.get_reaction_counts(story_id, db)

@router.get("/{story_id}/breakdown")
async def get_breakdown(
    story_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get reaction breakdown with percentages."""
    return await ReactionService.get_reaction_breakdown(story_id, db)
