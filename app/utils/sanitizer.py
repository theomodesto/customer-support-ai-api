import html
import re
from typing import Optional
from app.utils.logger import logger

class InputSanitizer:
    """Input sanitization utility to prevent XSS and injection attacks."""
    
    def __init__(self):
        # Patterns for potentially dangerous content
        self.script_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<form[^>]*>',
            r'<input[^>]*>',
            r'<textarea[^>]*>',
            r'<select[^>]*>',
            r'<button[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>',
        ]
        
        # SQL injection patterns (basic)
        self.sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b\s+.*\bfrom\b)',
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b\s+.*\bwhere\b)',
        ]
        
        # Compile patterns for efficiency
        self.script_regex = re.compile('|'.join(self.script_patterns), re.IGNORECASE | re.DOTALL)
        self.sql_regex = re.compile('|'.join(self.sql_patterns), re.IGNORECASE)
    
    def sanitize_text(self, text: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
        """
        Sanitize text input to prevent XSS and injection attacks.
        
        Args:
            text: The text to sanitize
            max_length: Maximum allowed length (truncates if exceeded)
            
        Returns:
            Sanitized text or None if input was None
        """
        if text is None:
            return None
        
        original_length = len(text)
        
        # Step 1: Remove dangerous HTML/script content
        sanitized = self._remove_dangerous_content(text)
        
        # Step 2: Escape HTML entities
        sanitized = html.escape(sanitized)
        
        # Step 3: Remove any remaining HTML tags
        sanitized = re.sub(r'<[^>]+>', '', sanitized)
        
        # Step 4: Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        # Step 5: Apply length limit if specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(
                "Text truncated due to length limit",
                component="sanitizer",
                original_length=original_length,
                truncated_length=len(sanitized),
                max_length=max_length
            )
        
        # Log if significant changes were made
        if len(sanitized) != original_length:
            logger.info(
                "Text sanitized",
                component="sanitizer",
                original_length=original_length,
                sanitized_length=len(sanitized),
                changes_made=True
            )
        
        return sanitized
    
    def _remove_dangerous_content(self, text: str) -> str:
        """Remove potentially dangerous content from text."""
        # Remove script patterns
        text = self.script_regex.sub('', text)
        
        # Remove SQL injection patterns (basic protection)
        text = self.sql_regex.sub('', text)
        
        # Remove other potentially dangerous patterns
        dangerous_patterns = [
            r'<[^>]*>',  # Any remaining HTML tags
            r'javascript:',  # JavaScript protocol
            r'vbscript:',  # VBScript protocol
            r'data:',  # Data URLs
            r'file:',  # File protocol
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def is_safe_content(self, text: Optional[str]) -> bool:
        """
        Check if content appears to be safe (no dangerous patterns detected).
        
        Args:
            text: Text to check
            
        Returns:
            True if content appears safe, False otherwise
        """
        if not text:
            return True
        
        # Check for dangerous patterns
        if self.script_regex.search(text):
            return False
        
        if self.sql_regex.search(text):
            return False
        
        # Check for other suspicious patterns
        suspicious_patterns = [
            r'<[^>]*>',  # HTML tags
            r'javascript:',  # JavaScript protocol
            r'vbscript:',  # VBScript protocol
            r'data:',  # Data URLs
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        
        return True

# Global sanitizer instance
sanitizer = InputSanitizer() 