"""
Notification service for Firebase Cloud Messaging.

Handles push notification registration, preferences, and digest generation.
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException

from app.models import Story

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification operations."""

    @staticmethod
    async def get_top_story_digest(db: AsyncSession) -> dict:
        """
        Get top story of the day for digest notification.

        Returns:
            Story with highest views and reactions

        Raises:
            HTTPException: If no published stories found
        """
        try:
            # Get top story based on views (simple scoring for now)
            result = await db.execute(
                select(Story)
                .where(Story.is_published == True)
                .order_by(Story.view_count.desc())
                .limit(1)
            )

            story = result.scalar_one_or_none()

            if not story:
                raise HTTPException(
                    status_code=404, detail="No published stories found"
                )

            return {
                "id": story.id,
                "title": story.summary or story.content[:100],
                "snippet": story.content[:150] + "..."
                if len(story.content) > 150
                else story.content,
                "category": story.category,
                "views": story.view_count,
                "summary": story.summary,
                "lessons": story.lessons,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting top story digest: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to get top story")

    @staticmethod
    async def get_daily_digest(db: AsyncSession) -> dict:
        """
        Get daily digest with top stories.

        Returns:
            List of top 5 stories from past 24 hours
        """
        from datetime import datetime, timedelta

        try:
            yesterday = datetime.utcnow() - timedelta(days=1)

            result = await db.execute(
                select(Story)
                .where(
                    (Story.is_published == True)
                    & (Story.created_at >= yesterday)
                )
                .order_by(Story.view_count.desc())
                .limit(5)
            )

            stories = result.scalars().all()

            return {
                "title": "Daily Story Digest",
                "stories": [
                    {
                        "id": s.id,
                        "summary": s.summary or s.content[:100],
                        "category": s.category,
                        "views": s.view_count,
                    }
                    for s in stories
                ],
                "count": len(stories),
            }

        except Exception as e:
            logger.error(f"Error getting daily digest: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to get daily digest"
            )

    @staticmethod
    async def validate_fcm_token(fcm_token: str) -> bool:
        """
        Validate FCM token format.

        Args:
            fcm_token: Firebase Cloud Messaging token

        Returns:
            True if valid format, False otherwise
        """
        return isinstance(fcm_token, str) and len(fcm_token) > 50
