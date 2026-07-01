"""
FinBuddy Security Enhancements

Provides PII redaction, rate limiting, audit logging, and field-level encryption
for sensitive financial data. Demonstrates security best practices for an AI agent
handling personal financial information.

Features:
  - PII Redaction: Automatically masks Aadhaar, PAN, bank account numbers, phone numbers, UPI IDs
  - Rate Limiting: Per-user request throttling via Redis-backed sliding window
  - Audit Logging: Immutable append-only log of all financial transactions and agent actions
  - Field Encryption: Symmetric Fernet encryption for sensitive DB columns
"""

import re
from typing import Optional, Dict, Any
from datetime import datetime
import json
import hashlib
import base64
from cryptography.fernet import Fernet

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# PII REDACTION
# =============================================================================

class PIIReductor:
    """
    Redacts Personally Identifiable Information (PII) from text strings.

    Patterns covered:
      - Indian Aadhaar numbers (12 digits, optionally spaced)
      - Indian PAN numbers (5 letters + 4 digits + 1 letter)
      - Bank account numbers (9-18 digits)
      - Indian phone numbers (+91, 10 digits)
      - UPI IDs (xxx@upi, xxx@oksbi, etc.)
      - Credit card numbers (13-19 digits, Luhn-like)
      - Debit card numbers (13-19 digits)
    """

    PATTERNS = {
        "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
        "pan": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
        "bank_account": re.compile(r"\b\d{9,18}\b"),
        "phone": re.compile(r"(?:\+91[-\s]?)?\d{10}\b"),
        "upi": re.compile(r"\b[\w.+-]+@[\w]+\b"),
        "card": re.compile(r"\b(?:\d{4}[-\s]?){3,4}\d{1,4}\b"),
    }

    @classmethod
    def redact(cls, text: str) -> str:
        """Redact all PII patterns from text, returning sanitized string."""
        if not text or not settings.PII_REDACTION_ENABLED:
            return text

        redacted = text
        for pii_type, pattern in cls.PATTERNS.items():
            redacted = pattern.sub(f"[REDACTED-{pii_type.upper()}]", redacted)
        return redacted

    @classmethod
    def redact_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact PII from a dictionary's string values."""
        if not isinstance(data, dict):
            return data
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = cls.redact(value)
            elif isinstance(value, dict):
                result[key] = cls.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [cls.redact(v) if isinstance(v, str) else v for v in value]
            else:
                result[key] = value
        return result


# =============================================================================
# RATE LIMITING
# =============================================================================

class RateLimiter:
    """
    Sliding-window rate limiter backed by Redis.
    Tracks requests per user_id and rejects if window is exceeded.
    """

    def __init__(self, redis_client=None):
        self.redis = redis_client
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.window_seconds = settings.RATE_LIMIT_WINDOW

    async def is_allowed(self, user_id: str) -> tuple[bool, Optional[int]]:
        """
        Check if user_id is within rate limit.

        Returns:
            (allowed: bool, remaining: int | None)
        """
        if not settings.RATE_LIMIT_ENABLED or self.redis is None:
            return True, None

        key = f"rate_limit:{user_id}"
        now = datetime.utcnow().timestamp()
        window_start = now - self.window_seconds

        # Remove old entries outside the window
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count current entries in window
        current_count = await self.redis.zcard(key)

        if current_count >= self.max_requests:
            remaining = 0
            return False, remaining

        # Add current request timestamp
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, self.window_seconds)

        remaining = self.max_requests - current_count - 1
        return True, remaining


# =============================================================================
# AUDIT LOGGING
# =============================================================================

class AuditLogger:
    """
    Immutable, append-only audit trail for all financial transactions and agent actions.

    Each entry is a JSON line with:
      - timestamp (UTC ISO8601)
      - user_id (hashed for privacy)
      - action_type (transaction, agent_run, login, data_export, etc.)
      - resource_type (transaction, investment, chat_message, etc.)
      - resource_id
      - actor (user_id or agent_name)
      - metadata (dict, PII-redacted)
      - checksum (SHA-256 of the serialized entry)
    """

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = log_path or "audit.log"
        self._enabled = settings.AUDIT_LOGGING_ENABLED

    def _hash_user_id(self, user_id: str) -> str:
        """Hash user_id for privacy in logs."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]

    def _compute_checksum(self, entry: Dict[str, Any]) -> str:
        """Compute SHA-256 checksum of the serialized entry."""
        canonical = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def log(self, *, action_type: str, resource_type: str, resource_id: str,
            actor: str, metadata: Optional[Dict[str, Any]] = None):
        """Append an audit entry."""
        if not self._enabled:
            return

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_hash": self._hash_user_id(actor),
            "action_type": action_type,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "actor": actor,  # Keep raw actor for internal use, hash in public views
            "metadata": PIIReductor.redact_dict(metadata or {}),
        }
        entry["checksum"] = self._compute_checksum({k: v for k, v in entry.items() if k != "checksum"})

        line = json.dumps(entry) + "\n"

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            logger.error("Audit log write failed", error=str(e))

        # Also log to structured logger
        logger.info(
            "Audit event recorded",
            action_type=action_type,
            resource_type=resource_type,
            user_hash=entry["user_hash"],
        )


# =============================================================================
# FIELD-LEVEL ENCRYPTION
# =============================================================================

class FieldEncryptor:
    """
    Symmetric encryption for sensitive database fields.
    Uses Fernet (AES-128 in CBC mode with HMAC) from the cryptography library.

    Fields to encrypt in production:
      - users.pan_number
      - users.aadhaar_hash
      - users.bank_account_number
      - transactions.merchant_details (if contains PII)
    """

    def __init__(self, key: Optional[str] = None):
        raw_key = key or settings.ENCRYPTION_KEY
        if not raw_key:
            # Generate a placeholder key for development (NOT for production)
            logger.warning("ENCRYPTION_KEY not set; using placeholder key. Set a strong 32-byte key in production.")
            raw_key = base64.urlsafe_b64encode(b"finbuddy_dev_key__32_bytes_long!").decode()

        # Ensure key is valid Fernet key (32 bytes, base64-encoded)
        try:
            self._fernet = Fernet(raw_key.encode() if isinstance(raw_key, str) else raw_key)
        except Exception:
            # Derive valid key from provided string
            derived = base64.urlsafe_b64encode(hashlib.sha256(raw_key.encode()).digest())
            self._fernet = Fernet(derived)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string. Returns base64-encoded ciphertext."""
        if not plaintext:
            return ""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64-encoded ciphertext. Returns plaintext string."""
        if not ciphertext:
            return ""
        return self._fernet.decrypt(ciphertext.encode()).decode()


# =============================================================================
# FACADE
# =============================================================================

class SecurityManager:
    """
    Unified security facade providing PII redaction, rate limiting,
    audit logging, and field encryption.

    Usage in FastAPI endpoints:
        security = SecurityManager(redis_client)
        allowed, remaining = await security.rate_limiter.is_allowed(user_id)
        if not allowed:
            raise HTTPException(429, "Rate limit exceeded")
        security.audit.log(action_type="transaction_create", ...)
    """

    def __init__(self, redis_client=None):
        self.redactor = PIIReductor()
        self.rate_limiter = RateLimiter(redis_client=redis_client)
        self.audit = AuditLogger()
        self.encryptor = FieldEncryptor()


# Singleton accessor (initialized with None, inject Redis in app startup)
_security_manager: Optional[SecurityManager] = None


def get_security_manager(redis_client=None) -> SecurityManager:
    """Get or create the global SecurityManager singleton."""
    global _security_manager
    if _security_manager is None or (redis_client is not None and _security_manager.rate_limiter.redis is None):
        _security_manager = SecurityManager(redis_client=redis_client)
    return _security_manager
