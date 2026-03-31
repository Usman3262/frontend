"""
Search routes.

Thin HTTP layer - delegates business logic to SearchService.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import SearchRequest, SearchResponse, SearchResult
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])

@router.post("", response_model=SearchResponse)
async def search(
    search: SearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search stories."""
    return await SearchService.search_stories(search, db)

@router.get("/categories", response_model=list[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    """Get available categories."""
    return await SearchService.get_categories(db)

@router.get("/trending", response_model=list[SearchResult])
async def get_trending(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get trending stories."""
    return await SearchService.get_trending_stories(limit, db)
