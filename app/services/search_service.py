"""
Search service layer.

Handles story search operations via Meilisearch with database fallback.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, desc
from datetime import datetime, timedelta

from app.models import Story, Reaction
from app.schemas import SearchRequest, SearchResult, SearchResponse, StoryListResponse, StoryListItemResponse
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class SearchService:
    """Service for search operations."""
    
    @staticmethod
    async def search_stories(
        search_data: SearchRequest,
        db: AsyncSession,
    ) -> SearchResponse:
        """
        Search stories using Meilisearch or database fallback.
        
        Args:
            search_data: Search request data
            db: Database session
        
        Returns:
            Search results
        """
        try:
            # Try Meilisearch first
            return await SearchService._meilisearch_search(search_data, db)
        except Exception as e:
            logger.warning(f"Meilisearch failed: {e}, falling back to database search")
            return await SearchService._database_search(search_data, db)
    
    @staticmethod
    async def _meilisearch_search(
        search_data: SearchRequest,
        db: AsyncSession,
    ) -> SearchResponse:
        """
        Search using Meilisearch.
        
        Args:
            search_data: Search request
            db: Database session
        
        Returns:
            Search results from Meilisearch
        """
        try:
            import meilisearch
            
            client = meilisearch.Client(
                settings.meilisearch_url,
                api_key=settings.meilisearch_api_key,
            )
            
            # Build search filter
            filters = None
            if search_data.category:
                filters = f"category = {search_data.category}"
            
            # Search
            search_results = client.index("stories").search(
                search_data.query,
                {
                    "filter": filters,
                    "limit": search_data.limit,
                    "offset": search_data.offset,
                }
            )
            
            # Extract story IDs
            story_ids = [int(hit["id"]) for hit in search_results.get("hits", [])]
            
            if not story_ids:
                return SearchResponse(
                    query=search_data.query,
                    total=0,
                    results=[],
                    limit=search_data.limit,
                    offset=search_data.offset,
                )
            
            # Fetch from database
            result = await db.execute(
                select(Story).where(
                    (Story.id.in_(story_ids)) & (Story.is_published == True)
                )
            )
            stories = result.scalars().all()
            
            results = [
                SearchResult(
                    id=story.id,
                    content=story.content,
                    category=story.category,
                    created_at=story.created_at,
                    view_count=story.view_count,
                )
                for story in stories
            ]
            
            return SearchResponse(
                query=search_data.query,
                total=search_results.get("estimatedTotalHits", len(results)),
                results=results,
                limit=search_data.limit,
                offset=search_data.offset,
            )
        
        except ImportError:
            raise RuntimeError("Meilisearch not installed")
        except Exception as e:
            raise RuntimeError(f"Meilisearch error: {e}")
    
    @staticmethod
    async def _database_search(
        search_data: SearchRequest,
        db: AsyncSession,
    ) -> SearchResponse:
        """
        Fallback search using database LIKE query.
        
        Args:
            search_data: Search request
            db: Database session
        
        Returns:
            Search results
        """
        query = select(Story).where(Story.is_published == True)
        
        # Apply category filter
        if search_data.category:
            query = query.where(Story.category == search_data.category)
        
        # Search in content
        search_term = f"%{search_data.query}%"
        query = query.where(
            or_(
                Story.content.ilike(search_term),
                Story.summary.ilike(search_term),
            )
        )
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Story.id)).where(
                Story.is_published == True
            ).where(
                or_(
                    Story.content.ilike(search_term),
                    Story.summary.ilike(search_term),
                )
            )
        )
        total = count_result.scalar() or 0
        
        # Apply pagination
        query = query.offset(search_data.offset).limit(search_data.limit)
        result = await db.execute(query)
        stories = result.scalars().all()
        
        results = [
            SearchResult(
                id=story.id,
                content=story.content,
                category=story.category,
                created_at=story.created_at,
                view_count=story.view_count,
            )
            for story in stories
        ]
        
        return SearchResponse(
            query=search_data.query,
            total=total,
            results=results,
            limit=search_data.limit,
            offset=search_data.offset,
        )
    
    @staticmethod
    async def get_trending_stories(
        limit: int,
        db: AsyncSession,
    ) -> list[SearchResult]:
        """
        Get trending stories (recent activity).
        
        Args:
            limit: Number of stories to return
            db: Database session
        
        Returns:
            List of trending stories
        """
        # Calculate trending window (last 24 hours)
        recent_time = datetime.utcnow() - timedelta(hours=24)
        
        result = await db.execute(
            select(Story)
            .where(Story.is_published == True)
            .where(Story.updated_at >= recent_time)
            .order_by(desc(Story.view_count))
            .limit(limit)
        )
        stories = result.scalars().all()
        
        return [
            SearchResult(
                id=story.id,
                content=story.content,
                category=story.category,
                created_at=story.created_at,
                view_count=story.view_count,
            )
            for story in stories
        ]
    
    @staticmethod
    async def get_categories(db: AsyncSession) -> list[str]:
        """
        Get all available story categories from database.
        
        Args:
            db: Database session
        
        Returns:
            List of unique categories
        """
        result = await db.execute(
            select(Story.category)
            .where(Story.category.isnot(None))
            .where(Story.is_published == True)
            .distinct()
            .order_by(Story.category)
        )
        categories = result.scalars().all()
        return list(categories)
    
    @staticmethod
    async def search_stories_with_filters(
        search_text: str,
        category: str | None,
        sort_by: str,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> StoryListResponse:
        """
        Search stories with full-text search and filters.
        
        Uses Meilisearch if available, falls back to database LIKE search.
        Returns stories in StoryListItemResponse format with snippets and reactions.
        
        Args:
            search_text: Full-text search query
            category: Optional category filter
            sort_by: Sort order ('new', 'top', 'trending')
            limit: Results limit (1-100)
            offset: Pagination offset
            db: Database session
        
        Returns:
            StoryListResponse with paginated search results
        """
        try:
            # Try Meilisearch first
            return await SearchService._meilisearch_search_with_filters(
                search_text, category, sort_by, limit, offset, db
            )
        except Exception as e:
            logger.warning(f"Meilisearch failed: {e}, falling back to database search")
            return await SearchService._database_search_with_filters(
                search_text, category, sort_by, limit, offset, db
            )
    
    @staticmethod
    async def _meilisearch_search_with_filters(
        search_text: str,
        category: str | None,
        sort_by: str,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> StoryListResponse:
        """
        Search using Meilisearch with filters and return StoryListResponse.
        """
        try:
            import meilisearch
            
            client = meilisearch.Client(
                settings.meilisearch_url,
                api_key=settings.meilisearch_api_key,
            )
            
            # Build search filter
            filters = None
            if category:
                filters = f"category = '{category}'"
            
            # Search
            search_results = client.index("stories").search(
                search_text,
                {
                    "filter": filters,
                    "limit": limit,
                    "offset": offset,
                }
            )
            
            # Extract story IDs
            story_ids = [int(hit["id"]) for hit in search_results.get("hits", [])]
            total = search_results.get("estimatedTotalHits", 0)
            
            if not story_ids:
                return StoryListResponse(
                    total=0,
                    limit=limit,
                    offset=offset,
                    stories=[],
                )
            
            # Fetch from database with proper ordering
            query = select(Story).where(
                (Story.id.in_(story_ids)) & (Story.is_published == True)
            )
            
            # Apply sorting
            if sort_by == "top":
                query = query.order_by(desc(Story.view_count))
            elif sort_by == "trending":
                query = query.order_by(desc(Story.updated_at), desc(Story.view_count))
            else:  # "new"
                query = query.order_by(desc(Story.created_at))
            
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
        
        except ImportError:
            raise RuntimeError("Meilisearch not installed")
        except Exception as e:
            raise RuntimeError(f"Meilisearch error: {e}")
    
    @staticmethod
    async def _database_search_with_filters(
        search_text: str,
        category: str | None,
        sort_by: str,
        limit: int,
        offset: int,
        db: AsyncSession,
    ) -> StoryListResponse:
        """
        Fallback search using database LIKE query with filters.
        Returns StoryListResponse format.
        """
        from sqlalchemy import or_
        
        query = select(Story).where(Story.is_published == True)
        
        # Apply category filter
        if category:
            query = query.where(Story.category == category)
        
        # Search in content, summary
        search_term = f"%{search_text}%"
        query = query.where(
            or_(
                Story.content.ilike(search_term),
                Story.summary.ilike(search_term),
                Story.lessons.ilike(search_term),
            )
        )
        
        # Get total count
        count_query = select(func.count(Story.id)).where(Story.is_published == True)
        if category:
            count_query = count_query.where(Story.category == category)
        count_query = count_query.where(
            or_(
                Story.content.ilike(search_term),
                Story.summary.ilike(search_term),
                Story.lessons.ilike(search_term),
            )
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
        
        # Apply pagination
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
    def index_story(story_id: int, title: str, content: str, category: str = None) -> bool:
        """
        Index a story in Meilisearch.
        
        Called when a story is published.
        
        Args:
            story_id: Story ID
            title: Story title/summary
            content: Story content
            category: Story category
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import meilisearch
            
            client = meilisearch.Client(
                settings.meilisearch_url,
                api_key=settings.meilisearch_api_key,
            )
            
            # Create or update document in Meilisearch
            document = {
                "id": str(story_id),
                "title": title or f"Story {story_id}",
                "content": content,
                "category": category or "general",
            }
            
            # Add to index
            response = client.index("stories").add_documents([document])
            logger.info(f"✅ Story {story_id} indexed in Meilisearch: {response}")
            return True
        
        except ImportError:
            logger.warning("Meilisearch not installed, skipping indexing")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to index story {story_id} in Meilisearch: {e}")
            return False
    
    @staticmethod
    def delete_story_from_index(story_id: int) -> bool:
        """
        Remove a story from Meilisearch index.
        
        Called when a story is deleted.
        
        Args:
            story_id: Story ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            import meilisearch
            
            client = meilisearch.Client(
                settings.meilisearch_url,
                api_key=settings.meilisearch_api_key,
            )
            
            # Delete from index
            response = client.index("stories").delete_document(str(story_id))
            logger.info(f"🗑️  Story {story_id} removed from Meilisearch")
            return True
        
        except ImportError:
            logger.warning("Meilisearch not installed, skipping index deletion")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to delete story {story_id} from Meilisearch: {e}")
            return False
