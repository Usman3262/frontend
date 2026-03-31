"""
Notification routes.

Thin HTTP layer - delegates business logic to NotificationService.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    FCMTokenRequest,
    NotificationPreferences,
    TopStoryDigestResponse,
    DailyDigestResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post("/register-token")
async def register_fcm_token(
    request: FCMTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register FCM token for push notifications.

    Args:
        request: FCM token from frontend
        db: Database session

    Returns:
        Success confirmation

    Note:
        In production, store token in database linked to user/session
        For MVP, we validate and acknowledge receipt
    """
    if not NotificationService.validate_fcm_token(request.fcm_token):
        return {"success": False, "message": "Invalid FCM token"}

    # In production, save to database:
    # db.add(FCMTokenModel(token=request.fcm_token))
    # await db.commit()

    return {
        "success": True,
        "message": "FCM token registered successfully",
        "fcm_token": request.fcm_token,
    }


@router.post("/unsubscribe")
async def unsubscribe_from_notifications(
    request: FCMTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Unsubscribe from push notifications.

    Args:
        request: FCM token to unsubscribe
        db: Database session

    Returns:
        Success confirmation

    Note:
        In production, delete token from database
    """
    # In production, remove from database:
    # await db.execute(delete(FCMTokenModel).where(FCMTokenModel.token == request.fcm_token))

    return {
        "success": True,
        "message": "Unsubscribed from notifications",
    }


@router.get("/top-story-digest", response_model=TopStoryDigestResponse)
async def get_top_story_digest(db: AsyncSession = Depends(get_db)):
    """
    Get top story of the day for digest notification.

    Returns:
        Top story with highest views and engagement
    """
    return await NotificationService.get_top_story_digest(db)


@router.get("/daily-digest", response_model=DailyDigestResponse)
async def get_daily_digest(db: AsyncSession = Depends(get_db)):
    """
    Get daily digest with top 5 stories from past 24 hours.

    Returns:
        List of top stories from today
    """
    return await NotificationService.get_daily_digest(db)


@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences():
    """
    Get current notification preferences.

    Returns:
        User's notification preference settings

    Note:
        In production, fetch from database with user authentication
        For MVP, return default preferences
    """
    return NotificationPreferences(
        enable_daily_digest=False,
        enable_top_story=False,
    )


@router.put("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    preferences: NotificationPreferences,
):
    """
    Update notification preferences.

    Args:
        preferences: Updated preference settings

    Returns:
        Confirmed updated preferences

    Note:
        In production, save preferences to database with user authentication
        For MVP, acknowledge and return settings
    """
    # In production:
    # db.add_or_update(UserNotificationPreferences(...))
    # await db.commit()

    return preferences
