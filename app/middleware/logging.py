import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from app.utils.logger import logger

async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to log API requests with timing and structured data.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or endpoint handler
        
    Returns:
        FastAPI response object
    """
    start_time = time.time()
    
    # Extract request details
    method = request.method
    path = request.url.path
    query_params = str(request.query_params) if request.query_params else ""
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request start
    logger.info(
        f"Request started: {method} {path}",
        component="api",
        method=method,
        path=path,
        query_params=query_params,
        user_agent=user_agent,
        client_ip=client_ip
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Log successful request
        logger.log_api_request(
            method=method,
            path=path,
            status_code=response.status_code,
            processing_time_ms=processing_time,
            user_agent=user_agent,
            client_ip=client_ip,
            query_params=query_params
        )
        
        return response
        
    except Exception as e:
        # Calculate processing time for failed requests
        processing_time = int((time.time() - start_time) * 1000)
        
        # Log failed request
        logger.error(
            f"Request failed: {method} {path}",
            component="api",
            method=method,
            path=path,
            status_code=500,
            processing_time_ms=processing_time,
            user_agent=user_agent,
            client_ip=client_ip,
            query_params=query_params,
            error_type=type(e).__name__,
            error_message=str(e)
        )
        
        # Re-raise the exception
        raise 