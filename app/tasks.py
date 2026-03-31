"""
Celery background tasks for async operations.

Tasks:
- Story moderation
- Story summarization
- Daily digest generation
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "lifeecho",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_pool="threads",  # Use threads pool on Windows to avoid billiard issues
)

# ===================== TASKS =====================

@celery_app.task(bind=True, name="moderate_story")
def moderate_story(self, story_id: int, max_retries: int = 3):
    """
    Moderate story content using AI.
    
    Checks for offensive language, spam, adult content, etc.
    
    Args:
        story_id: Story ID to moderate
        max_retries: Number of retries on failure
    """
    try:
        logger.info(f"Moderating story {story_id}")
        
        # TODO: Implement AI moderation
        # from app.utils.ai import moderate_content
        # is_safe, reason = await moderate_content(story.content)
        # update_story_moderation(story_id, "approved" if is_safe else "rejected")
        
        logger.info(f"Story {story_id} moderation completed")
    
    except Exception as exc:
        logger.error(f"Error moderating story {story_id}: {exc}")
        if self.request.retries < max_retries:
            raise self.retry(countdown=60)
        else:
            logger.error(f"Failed to moderate story {story_id} after {max_retries} retries")

@celery_app.task(bind=True, name="summarize_story")
def summarize_story(self, story_id: int):
    """
    Generate AI summary of story content.
    
    Args:
        story_id: Story ID to summarize
    """
    try:
        logger.info(f"Summarizing story {story_id}")
        
        # TODO: Implement AI summarization
        # from app.utils.ai import summarize_story
        # summary = await summarize_story(story.content)
        # update_story_summary(story_id, summary)
        
        logger.info(f"Story {story_id} summarization completed")
    
    except Exception as exc:
        logger.error(f"Error summarizing story {story_id}: {exc}")
        if self.request.retries < 2:
            raise self.retry(countdown=60)

@celery_app.task(bind=True, name="extract_story_lessons")
def extract_story_lessons(self, story_id: int):
    """
    Extract key life lessons from story using AI.
    
    Args:
        story_id: Story ID to process
    """
    try:
        logger.info(f"Extracting lessons from story {story_id}")
        
        # TODO: Implement lesson extraction
        # from app.utils.ai import extract_lessons
        # lessons = await extract_lessons(story.content)
        # update_story_lessons(story_id, lessons)
        
        logger.info(f"Lessons extracted from story {story_id}")
    
    except Exception as exc:
        logger.error(f"Error extracting lessons from story {story_id}: {exc}")
        if self.request.retries < 2:
            raise self.retry(countdown=60)

@celery_app.task(name="generate_daily_digest")
def generate_daily_digest():
    """
    Generate daily digest of top stories.
    
    Scheduled daily at 8 AM UTC.
    """
    try:
        logger.info("Generating daily digest")
        
        # TODO: Implement digest generation
        # top_stories = get_top_stories_today()
        # digest = create_digest_email(top_stories)
        # send_notification(digest)
        
        logger.info("Daily digest generated")
    
    except Exception as exc:
        logger.error(f"Error generating daily digest: {exc}")

@celery_app.task(name="cleanup_cache")
def cleanup_cache():
    """
    Clean up expired cache entries.
    
    Scheduled every 6 hours.
    """
    try:
        logger.info("Cleaning up cache")
        
        # TODO: Implement cache cleanup
        # redis_client = get_redis_client()
        # redis_client.delete_expired_keys()
        
        logger.info("Cache cleanup completed")
    
    except Exception as exc:
        logger.error(f"Error during cache cleanup: {exc}")

@celery_app.task(name="process_story_event")
def process_story_event(story_id: int, event_type: str):
    """
    Process story events (published, deleted, updated, etc).
    
    Args:
        story_id: Story ID
        event_type: Type of event (published, deleted, updated)
    """
    try:
        from app.services.search_service import SearchService
        from app.database import AsyncSessionLocal
        from sqlalchemy import select
        from app.models import Story
        import asyncio
        
        logger.info(f"Processing story event: {event_type} for story {story_id}")
        
        if event_type == "published":
            # Fetch story from database and index it
            async def fetch_and_index():
                async with AsyncSessionLocal() as db:
                    try:
                        result = await db.execute(
                            select(Story).where(Story.id == story_id)
                        )
                        story = result.scalar_one_or_none()
                        
                        if story:
                            # Index in Meilisearch (sync function)
                            SearchService.index_story(
                                story_id=story.id,
                                title=story.summary or f"Story {story.id}",
                                content=story.content,
                                category=story.category
                            )
                            logger.info(f"✅ Story {story_id} published and indexed in Meilisearch")
                        else:
                            logger.error(f"Story {story_id} not found in database")
                    except Exception as e:
                        logger.error(f"Error fetching story {story_id}: {e}")
            
            # Run async operation
            try:
                # Try running with asyncio.run() if no event loop
                asyncio.run(fetch_and_index())
            except RuntimeError as e:
                if "asyncio.run() cannot be called from a running event loop" in str(e):
                    # If event loop is already running, create a task
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(fetch_and_index())
                else:
                    raise
            
        elif event_type == "updated":
            logger.info(f"📝 Story {story_id} updated")
            # TODO: Update in Meilisearch if needed
            
        elif event_type == "deleted":
            # Remove from Meilisearch (sync function)
            SearchService.delete_story_from_index(story_id)
            logger.info(f"🗑️  Story {story_id} deleted and removed from Meilisearch index")
        
        logger.info(f"✅ Story event processed: {event_type} for story {story_id}")
    
    except Exception as exc:
        logger.error(f"Error processing story event: {exc}")

# ===================== CELERY BEAT SCHEDULE =====================

celery_app.conf.beat_schedule = {
    "generate-daily-digest": {
        "task": "generate_daily_digest",
        "schedule": crontab(hour=8, minute=0),  # 8 AM UTC
    },
    "cleanup-cache": {
        "task": "cleanup_cache",
        "schedule": crontab(hour="*/6"),  # Every 6 hours
    },
}
