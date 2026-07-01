"""
Structured logging configuration
"""

import sys
import logging
from typing import Any, Dict

import structlog
from structlog.types import Processor

from app.config import settings


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Determine if we're in JSON mode
    json_logs = settings.LOG_FORMAT == "json"
    
    # Shared processors
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]
    
    if json_logs:
        # JSON logging for production
        shared_processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()
    else:
        # Console logging for development
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    level_raw = settings.LOG_LEVEL
    level = logging.INFO
    try:
        if isinstance(level_raw, int):
            level = level_raw
        else:
            level_str = str(level_raw).upper().strip()
            if level_str.isdigit():
                level = int(level_str)
            else:
                level = getattr(logging, level_str, logging.INFO)
    except Exception:
        level = logging.INFO
    root_logger.setLevel(level)
    
    # Quiet noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding log context."""
    
    def __init__(self, **kwargs: Any):
        self.context = kwargs
    
    def __enter__(self):
        structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    user_id: str = None
) -> None:
    """Log HTTP request details."""
    logger = get_logger("http")
    
    log_data: Dict[str, Any] = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration_ms, 2),
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if status_code >= 500:
        logger.error("Request failed", **log_data)
    elif status_code >= 400:
        logger.warning("Request error", **log_data)
    else:
        logger.info("Request completed", **log_data)
