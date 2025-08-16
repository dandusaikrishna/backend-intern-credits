"""
Utility functions for the application
"""
import logging
import asyncio
import threading
import schedule
import time
from datetime import datetime, timezone
from src.database import db
from src.services import credit_service

logger = logging.getLogger(__name__)

class BackgroundScheduler:
    """Background job scheduler for daily tasks"""
    
    @staticmethod
    def daily_credit_bonus():
        """Add 5 credits to all users daily"""
        asyncio.run(BackgroundScheduler._run_daily_credit_bonus())
    
    @staticmethod
    async def _run_daily_credit_bonus():
        """Async function to run daily credit bonus"""
        logger.info("Running daily credit bonus job...")
        
        try:
            # Get all users
            users = await db.fetch("SELECT user_id FROM users")
            
            for user in users:
                user_id = user['user_id']
                
                # Add 5 credits
                await credit_service.add_credits(user_id, 5)
                
                # Log transaction
                await credit_service.log_transaction(
                    user_id, 5, 'DAILY_BONUS', 'Daily automatic credit bonus'
                )
            
            logger.info(f"Daily bonus applied to {len(users)} users")
            
        except Exception as e:
            logger.error(f"Error in daily credit bonus job: {e}")
    
    @staticmethod
    def run_scheduler():
        """Run the background scheduler"""
        schedule.every().day.at("00:00").do(BackgroundScheduler.daily_credit_bonus)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    @staticmethod
    def start_scheduler_thread():
        """Start scheduler in a separate thread"""
        scheduler_thread = threading.Thread(
            target=BackgroundScheduler.run_scheduler, 
            daemon=True
        )
        scheduler_thread.start()
        return scheduler_thread
