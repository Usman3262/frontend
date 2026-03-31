"""
Authentication service layer.

Handles user registration, authentication, anonymous number generation, and password hashing.
"""

import bcrypt
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models import AnonymousUser
from app.utils.validators import validate_password
from app.utils.constants import ERROR_USER_NOT_FOUND, ERROR_INVALID_CREDENTIALS
from app.schemas import UserAuthRequest, UserResponse

class AuthService:
    """Service for authentication operations."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        
        Raises:
            ValueError: If password doesn't meet requirements
        """
        is_valid, error = validate_password(password)
        if not is_valid:
            raise ValueError(error)
        
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Bcrypt hash
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False
    
    @staticmethod
    def generate_anonymous_number() -> str:
        """
        Generate a unique anonymous user number.
        
        Format: #XXXX where X is a digit (0-9)
        Example: #4821
        
        Returns:
            Anonymous number string
        
        Note:
            Uniqueness must be verified in database.
        """
        random_num = random.randint(0, 9999)
        return f"#{random_num:04d}"
    
    @staticmethod
    def generate_random_password() -> str:
        """
        Generate a secure random password meeting strength requirements.
        
        Requirements:
        - 12 characters minimum
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 digit
        - Mix of letters and numbers
        
        Returns:
            Random password string
        """
        import string
        
        # Ensure we have required character types
        password_chars = [
            random.choice(string.ascii_uppercase),  # At least 1 uppercase
            random.choice(string.ascii_lowercase),  # At least 1 lowercase
            random.choice(string.digits),            # At least 1 digit
        ]
        
        # Fill remaining with random chars from all sets
        all_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
        for _ in range(9):  # 12 total - 3 required = 9 more
            password_chars.append(random.choice(all_chars))
        
        # Shuffle to avoid predictable pattern
        random.shuffle(password_chars)
        
        return "".join(password_chars)
    
    @staticmethod
    async def signup(
        password: str,
        db: AsyncSession,
    ) -> UserResponse:
        """
        Register a new anonymous user.
        
        Args:
            password: User's password
            db: Database session
        
        Returns:
            UserResponse with created user details
        
        Raises:
            ValueError: If password invalid
            HTTPException: If registration fails
        """
        # Validate password
        is_valid, error = validate_password(password)
        if not is_valid:
            raise ValueError(error)
        
        # Generate unique anonymous number
        while True:
            anon_number = AuthService.generate_anonymous_number()
            result = await db.execute(
                select(AnonymousUser).where(
                    AnonymousUser.anonymous_number == anon_number
                )
            )
            if not result.scalar_one_or_none():
                break  # Unique number found
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user
        user = AnonymousUser(
            anonymous_number=anon_number,
            password_hash=password_hash,
            is_active=True,
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    async def authenticate(
        auth: UserAuthRequest,
        db: AsyncSession,
    ) -> UserResponse:
        """
        Authenticate a user and return their information.
        
        Args:
            auth: Authentication credentials
            db: Database session
        
        Returns:
            UserResponse if successful
        
        Raises:
            HTTPException: If authentication fails
        """
        # Find user
        result = await db.execute(
            select(AnonymousUser).where(
                AnonymousUser.anonymous_number == auth.anonymous_number
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=ERROR_USER_NOT_FOUND)
        
        # Verify password
        if not AuthService.verify_password(auth.password, user.password_hash):
            raise HTTPException(status_code=401, detail=ERROR_INVALID_CREDENTIALS)
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    async def get_user_by_number(
        anonymous_number: str,
        db: AsyncSession,
    ) -> AnonymousUser | None:
        """
        Get user by anonymous number.
        
        Args:
            anonymous_number: User's anonymous number
            db: Database session
        
        Returns:
            AnonymousUser or None if not found
        """
        result = await db.execute(
            select(AnonymousUser).where(
                AnonymousUser.anonymous_number == anonymous_number
            )
        )
        return result.scalar_one_or_none()
