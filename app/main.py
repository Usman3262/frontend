"""
FastAPI application factory and main entry point.

Initializes:
- FastAPI app with middleware
- Route registration
- Error handlers
- Database lifecycle
- Auth endpoints
"""

from contextlib import asynccontextmanager
import logging
from typing import Dict

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db, init_db
from app.schemas import UserSignupRequest, UserAuthRequest, UserResponse
from app.services.auth_service import AuthService
from app.routes import story, reaction, search, notification

logger = logging.getLogger(__name__)
settings = get_settings()

# ===================== STARTUP/SHUTDOWN =====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Initializing LifeEcho API...")
    try:
        await init_db()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down LifeEcho API...")

# ===================== FASTAPI APP =====================

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title="LifeEcho API",
        description="Anonymous life stories platform with AI-powered insights",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # ========== MIDDLEWARE ==========
    
    # CORS middleware - allow frontend requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware - prevent Host header attacks
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
    
    # ========== EXCEPTION HANDLERS ==========
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with consistent response format."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.detail,
                "path": str(request.url.path),
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "path": str(request.url.path),
            },
        )
    
    # ========== HEALTH CHECK ==========
    
    @app.get("/health", tags=["health"])
    async def health_check() -> Dict[str, str]:
        """
        Health check endpoint.
        
        Returns:
            dict: Health status
        """
        return {
            "status": "healthy",
            "service": "LifeEcho API",
            "version": "1.0.0",
        }
    
    # ========== AUTH ENDPOINTS ==========
    
    @app.post("/auth/signup", response_model=UserResponse, tags=["auth"])
    async def signup(request: UserSignupRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
        """
        Create new anonymous user.
        
        Args:
            request: Signup request with password
            db: Database session
        
        Returns:
            UserResponse: New user details
        
        Raises:
            HTTPException: If signup fails
        """
        try:
            user = await AuthService.signup(request.password, db)
            logger.info(f"New user created: {user.anonymous_number}")
            return user
        except ValueError as e:
            logger.warning(f"Signup failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Signup error: {e}")
            raise HTTPException(status_code=500, detail="Signup failed")
    
    @app.post("/auth/login", response_model=UserResponse, tags=["auth"])
    async def login(request: UserAuthRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
        """
        Authenticate user.
        
        Args:
            request: Login request with anonymous_number and password
            db: Database session
        
        Returns:
            UserResponse: Authenticated user details
        
        Raises:
            HTTPException: If authentication fails
        """
        try:
            user = await AuthService.authenticate(request, db)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            logger.info(f"User authenticated: {user.anonymous_number}")
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(status_code=500, detail="Authentication failed")
    
    @app.get("/auth/me", response_model=UserResponse, tags=["auth"])
    async def get_current_user(
        anonymous_number: str,
        db: AsyncSession = Depends(get_db)
    ) -> UserResponse:
        """
        Get current user information.
        
        Args:
            anonymous_number: User's anonymous number (#XXXX format)
            db: Database session
        
        Returns:
            UserResponse: User details
        
        Raises:
            HTTPException: If user not found
        """
        try:
            user = await AuthService.get_user_by_number(anonymous_number, db)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return UserResponse(
                anonymous_number=user.anonymous_number,
                created_at=user.created_at,
                is_active=user.is_active,
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch user")
    
    # ========== ROUTE REGISTRATION ==========
    
    # Story routes (prefix already "/stories" in route file)
    app.include_router(
        story.router,
        prefix="/api/v1",
    )
    
    # Reaction routes (prefix already "/reactions" in route file)
    app.include_router(
        reaction.router,
        prefix="/api/v1",
    )
    
    # Search routes (prefix already "/search" in route file)
    app.include_router(
        search.router,
        prefix="/api/v1",
    )
    
    # Notification routes (prefix already "/notifications" in route file)
    app.include_router(
        notification.router,
        prefix="/api/v1",
    )
    
    logger.info("FastAPI application initialized successfully")
    return app

# ===================== APP INSTANCE =====================

app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info",
    )
