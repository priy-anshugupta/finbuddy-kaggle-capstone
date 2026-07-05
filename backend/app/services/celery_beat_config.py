"""
Celery Beat schedule configuration for periodic tasks
"""

from celery.schedules import crontab
from app.services.celery_app import celery_app


# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    # Daily market summary - 9 AM IST
    'daily-market-summary': {
        'task': 'daily_market_summary',
        'schedule': crontab(hour=3, minute=30),  # 3:30 AM UTC = 9:00 AM IST
    },
    
    # Nightly cash check - 11 PM IST
    'nightly-cash-check': {
        'task': 'nightly_cash_check',
        'schedule': crontab(hour=17, minute=30),  # 5:30 PM UTC = 11:00 PM IST
    },
}

celery_app.conf.timezone = 'Asia/Kolkata'
