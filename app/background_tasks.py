"""
Simple Redis-based task queue (replaces Celery for development).

This module provides lightweight background tasks using Redis
without the Python 3.14 compatibility issues of Celery.
"""

import json
import logging
import asyncio
from datetime import datetime
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SimpleTaskQueue:
    """Simple Redis-based task queue for background events."""
    
    @staticmethod
    async def publish_story_event(story_id: int, event_type: str) -> bool:
        """
        Publish a story event to Redis (non-blocking).
        
        Args:
            story_id: ID of the story
            event_type: Type of event (published, deleted, etc)
        
        Returns:
            True if published, False if error
        """
        try:
            import redis.asyncio as redis
            
            # Parse Redis URL
            redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Create event payload
            event = {
                "story_id": story_id,
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Push to Redis list (non-blocking)
            await redis_client.lpush(
                "story_events",
                json.dumps(event)
            )
            
            await redis_client.close()
            logger.debug(f"Published story event: {event_type} for story {story_id}")
            return True
            
        except Exception as e:
            logger.debug(f"Could not publish to Redis: {e}")
            return False
    
    @staticmethod
    async def publish_reaction_event(story_id: int, reaction_type: str) -> bool:
        """
        Publish a reaction event to Redis (non-blocking).
        
        Args:
            story_id: ID of the story
            reaction_type: Type of reaction
        
        Returns:
            True if published, False if error
        """
        try:
            import redis.asyncio as redis
            
            redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            event = {
                "story_id": story_id,
                "reaction_type": reaction_type,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            await redis_client.lpush(
                "reaction_events",
                json.dumps(event)
            )
            
            await redis_client.close()
            logger.debug(f"Published reaction event: {reaction_type} for story {story_id}")
            return True
            
        except Exception as e:
            logger.debug(f"Could not publish reaction to Redis: {e}")
            return False
    
    @staticmethod
    async def consume_events(queue_name: str, max_events: int = 100) -> list:
        """
        Consume events from a Redis list.
        
        Args:
            queue_name: Name of the Redis list
            max_events: Maximum events to consume
        
        Returns:
            List of event dictionaries
        """
        try:
            import redis.asyncio as redis
            
            redis_client = await redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            events = []
            for _ in range(max_events):
                event_json = await redis_client.rpop(queue_name)
                if not event_json:
                    break
                events.append(json.loads(event_json))
            
            await redis_client.close()
            return events
            
        except Exception as e:
            logger.warning(f"Could not consume from Redis: {e}")
            return []


# Celery tasks for background processing (optional, for when Celery is set up)
try:
    from app.tasks import moderate_story, send_digest_email
    HAS_CELERY = True
except (ImportError, Exception):
    HAS_CELERY = False
    logger.info("Celery not available - using simple Redis queue for background tasks")


async def queue_story_moderation(story_id: int) -> bool:
    """
    Queue a story for AI moderation (uses Celery if available, else Redis).
    
    Args:
        story_id: ID of the story to moderate
    
    Returns:
        True if queued successfully
    """
    if HAS_CELERY:
        try:
            moderate_story.delay(story_id)
            logger.info(f"Queued story {story_id} for Celery moderation")
            return True
        except Exception as e:
            logger.warning(f"Celery moderation failed, falling back: {e}")
    
    # Fall back to Redis event
    return await SimpleTaskQueue.publish_story_event(story_id, "moderation_pending")
