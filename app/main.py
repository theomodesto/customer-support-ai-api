from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.config import settings
from app.routes import support_requests, stats
from app.middleware.logging import logging_middleware
from app.utils.logger import logger
from fastapi.middleware.cors import CORSMiddleware



# Create database tables
# Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="""
    AI-Powered Customer Support Intelligence API

    This API processes customer support requests using AI to automatically:
    - Classify requests as technical, billing, or general inquiries
    - Generate confidence_score scores based on classification certainty
    - Create summaries for quick triage
    - Provide analytics and insights

    ## Features
    - **Automatic Classification**: AI-powered categorization of support requests
    - **Flexible Input**: Accept either free-form text or structured subject/body
    - **Real-time Processing**: Immediate AI analysis upon request creation
    - **Rich Filtering**: Query requests by category, priority, and other criteria
    - **Analytics Dashboard**: Statistics and insights for support trends
    - **Dataset Integration**: Pre-loaded with realistic customer support data
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add logging middleware
app.middleware("http")(logging_middleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: Change to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"Starting app..")

# Include routers
app.include_router(support_requests.router)
app.include_router(stats.router)

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify API is running."""
    return {
        "status": "healthy",
        "version": settings.version,
        "service": settings.app_name
    }

# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "Customer Support AI API",
        "version": settings.version,
        "docs": "/docs",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    # Log the error with structured data
    logger.error(
        f"Unhandled exception: {str(exc)}",
        component="api",
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    if settings.debug:
        # In debug mode, show full error details
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Internal server error: {str(exc)}",
                "error_type": type(exc).__name__
            }
        )
    else:
        # In production, show generic error message
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 