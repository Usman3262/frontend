"""
Simple background task queue using Redis.

Alternative to Celery that works with Python 3.14.
Stores simple tasks in Redis with no scheduler overhead.
"""

import json
import logging
from datetime import datetime
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SimpleTaskQueue:
    """Simple Redis-based task queue without Celery."""
    
    @staticmethod
    async def publish_story_event(story_id: int, event_type: str = "published"):
        """
        Publish a story event to Redis (non-blocking).
        
        Args:
            story_id: ID of the story
            event_type: Type of event (published, moderated, trending, etc)
        """
        try:
            import redis.asyncio as redis
            
            r = redis.from_url(settings.redis_url, decode_responses=True)
            
            event = {
                "story_id": story_id,
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Push to Redis list (queue)
            await r.lpush(f"story_events:{event_type}", json.dumps(event))
            
            # Set expiry (24 hours)
            await r.expire(f"story_events:{event_type}", 86400)
            
            logger.debug(f"Story event published: {story_id} -> {event_type}")
            await r.close()
            
        except Exception as e:
            logger.debug(f"Could not publish event to Redis (non-blocking): {e}")
    
    @staticmethod
    async def queue_notification(user_id: int, notification_type: str, data: dict):
        """
        Queue a notification to Redis for async processing.
        
        Args:
            user_id: User to notify  
            notification_type: Type of notification
            data: Notification data
        """
        try:
            import redis.asyncio as redis
            
            r = redis.from_url(settings.redis_url, decode_responses=True)
            
            notification = {
                "user_id": user_id,
                "type": notification_type,
                "data": data,
                "created_at": datetime.utcnow().isoformat(),
            }
            
            await r.lpush("notifications_queue", json.dumps(notification))
            await r.expire("notifications_queue", 604800)  # 7 days
            
            logger.debug(f"Notification queued for user {user_id}")
            await r.close()
            
        except Exception as e:
            logger.debug(f"Could not queue notification (non-blocking): {e}")
