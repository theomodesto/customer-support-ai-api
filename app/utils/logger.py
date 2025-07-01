import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from app.config import settings

class StructuredLogger:
    """Structured logging utility for consistent log formatting."""
    
    def __init__(self, name: str = "customer_support_ai"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure logger with JSON formatting for production."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            
            if settings.debug:
                # Human-readable format for development
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )
            else:
                # JSON format for production
                formatter = logging.Formatter('%(message)s')
            
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def _format_log_entry(
        self, 
        level: str, 
        message: str, 
        component: str,
        **kwargs
    ) -> str:
        """Format log entry as JSON for production or plain text for development."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "component": component,
            "message": message,
            **kwargs
        }
        
        if settings.debug:
            return f"{log_entry['timestamp']} - {level.upper()} - {component}: {message}"
        else:
            return json.dumps(log_entry)
    
    def info(self, message: str, component: str = "general", **kwargs):
        """Log info message with structured data."""
        log_message = self._format_log_entry("INFO", message, component, **kwargs)
        self.logger.info(log_message)
    
    def warning(self, message: str, component: str = "general", **kwargs):
        """Log warning message with structured data."""
        log_message = self._format_log_entry("WARNING", message, component, **kwargs)
        self.logger.warning(log_message)
    
    def error(self, message: str, component: str = "general", **kwargs):
        """Log error message with structured data."""
        log_message = self._format_log_entry("ERROR", message, component, **kwargs)
        self.logger.error(log_message)
    
    def critical(self, message: str, component: str = "general", **kwargs):
        """Log critical message with structured data."""
        log_message = self._format_log_entry("CRITICAL", message, component, **kwargs)
        self.logger.critical(log_message)

    def debug(self, message: str, component: str = "general", **kwargs):
        """Log debug message with structured data."""
        log_message = self._format_log_entry("DEBUG", message, component, **kwargs)
        self.logger.debug(log_message)
    
    def log_ml_error(
        self, 
        error: Exception, 
        context: Dict[str, Any],
        component: str = "ai_classification"
    ):
        """Log ML processing errors with detailed context."""
        self.error(
            message=f"ML processing failed: {str(error)}",
            component=component,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context
        )
    
    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        processing_time_ms: Optional[int] = None,
        user_agent: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Log API request details."""
        self.info(
            message=f"API Request: {method} {path} - {status_code}",
            component="api",
            method=method,
            path=path,
            status_code=status_code,
            processing_time_ms=processing_time_ms,
            user_agent=user_agent,
            error=error,
            **kwargs
        )

    def log_api_error(
        self,
        method: str,
        path: str,
        status_code: int,
        processing_time_ms: Optional[int] = None,
        user_agent: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """Log API request details."""
        self.error(
            message=f"API Error: {method} {path} - {status_code}",
            component="api",
            method=method,
            path=path,
            status_code=status_code,
            processing_time_ms=processing_time_ms,
            user_agent=user_agent,
            error=error,
            **kwargs
        )
    
    
    def log_database_operation(
        self,
        operation: str,
        table: str,
        processing_time_ms: int,
        success: bool,
        **kwargs
    ):
        """Log database operation details."""
        level = "INFO" if success else "ERROR"
        message = f"Database {operation} on {table}"
        
        if level == "INFO":
            self.info(
                message=message,
                component="database",
                operation=operation,
                table=table,
                processing_time_ms=processing_time_ms,
                success=success,
                **kwargs
            )
        else:
            self.error(
                message=message,
                component="database",
                operation=operation,
                table=table,
                processing_time_ms=processing_time_ms,
                success=success,
                **kwargs
            )

# Global logger instance
logger = StructuredLogger() 