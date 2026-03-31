"""
AI utilities for story processing.

Handles summarization and lesson extraction using OpenAI API.
"""

import logging
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

async def summarize_story(content: str, max_tokens: int = 100) -> str:
    """
    Summarize a story using OpenAI API.
    
    Args:
        content: Story content to summarize
        max_tokens: Maximum tokens for summary
    
    Returns:
        Summarized story text
    """
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured, skipping summarization")
        return None
    
    try:
        # TODO: Implement with OpenAI API
        # import openai
        # response = openai.ChatCompletion.create(
        #     model=settings.openai_model,
        #     messages=[{
        #         "role": "user",
        #         "content": f"Summarize this in {max_tokens} tokens: {content}"
        #     }]
        # )
        # return response.choices[0].message.content
        
        logger.info(f"Summarizing story ({len(content)} chars)")
        return None
    
    except Exception as e:
        logger.error(f"Error summarizing story: {e}")
        return None

async def extract_lessons(content: str) -> str:
    """
    Extract key lessons from story using OpenAI API.
    
    Args:
        content: Story content
    
    Returns:
        Extracted lessons as text
    """
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured, skipping lesson extraction")
        return None
    
    try:
        # TODO: Implement with OpenAI API
        # import openai
        # response = openai.ChatCompletion.create(
        #     model=settings.openai_model,
        #     messages=[{
        #         "role": "user",
        #         "content": f"Extract 2-3 key life lessons from this: {content}"
        #     }]
        # )
        # return response.choices[0].message.content
        
        logger.info(f"Extracting lessons from story ({len(content)} chars)")
        return None
    
    except Exception as e:
        logger.error(f"Error extracting lessons: {e}")
        return None

async def moderate_content(content: str) -> tuple[bool, str]:
    """
    Moderate content using OpenAI Moderation API.
    
    Args:
        content: Content to moderate
    
    Returns:
        Tuple of (is_safe, reason)
    """
    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured, assuming content is safe")
        return True, ""
    
    try:
        # TODO: Implement with OpenAI Moderation API
        # import openai
        # response = openai.Moderation.create(input=content)
        # flagged = response.results[0].flagged
        # categories = response.results[0].categories
        # if flagged:
        #     return False, str(categories)
        # return True, ""
        
        logger.info(f"Moderating content ({len(content)} chars)")
        return True, ""
    
    except Exception as e:
        logger.error(f"Error during moderation: {e}")
        # Default to safe on API errors
        return True, ""
