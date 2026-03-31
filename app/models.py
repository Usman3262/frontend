"""
SQLAlchemy ORM models for LifeEcho database schema.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class AnonymousUser(Base):
    """
    Anonymous user identity (no email required).
    
    Fields:
        id: Unique database identifier
        anonymous_number: Public-facing ID (e.g., "#4821")
        password_hash: Bcrypt hashed password
        created_at: Account creation timestamp
        is_active: Whether account is active
    """
    __tablename__ = "anonymous_users"
    
    id = Column(Integer, primary_key=True, index=True)
    anonymous_number = Column(String(10), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    stories = relationship("Story", back_populates="author", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user")


class Story(Base):
    """
    Anonymous life story submission.
    
    Fields:
        id: Unique identifier
        author_id: Foreign key to AnonymousUser
        content: Story text (10-2000 characters)
        category: Story category type
        image_url: Optional Cloudinary image URL
        summary: AI-generated summary
        is_published: Whether visible in feed
        moderation_status: pending, approved, rejected
        created_at, updated_at: Timestamps
        view_count: Number of views
    """
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("anonymous_users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    lessons = Column(Text, nullable=True)  # AI-extracted key lessons
    is_published = Column(Boolean, default=False)
    moderation_status = Column(String(20), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    view_count = Column(Integer, default=0)
    
    # Relationships
    author = relationship("AnonymousUser", back_populates="stories")
    reactions = relationship("Reaction", back_populates="story", cascade="all, delete-orphan")


class Reaction(Base):
    """
    Emotional reaction to a story.
    
    Fields:
        id: Unique identifier
        story_id: Foreign key to Story
        user_id: Foreign key to AnonymousUser (nullable for anonymous reactions)
        reaction_type: Type of reaction (Relatable, Inspired, StayStrong, Helpful)
        created_at: Reaction timestamp
    """
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("anonymous_users.id", ondelete="SET NULL"), nullable=True)
    reaction_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    story = relationship("Story", back_populates="reactions")
    user = relationship("AnonymousUser", back_populates="reactions")
