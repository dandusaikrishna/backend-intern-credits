"""
Business logic services for credit management
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from src.database import db
from src.schemas import UserCreditsResponse, TransactionLog

logger = logging.getLogger(__name__)

class CreditService:
    """Service class for credit management operations"""
    
    async def user_exists(self, user_id: int) -> bool:
        """Check if user exists in database"""
        result = await db.fetchval(
            "SELECT 1 FROM users WHERE user_id = $1", 
            user_id
        )
        return result is not None
    
    async def get_user_credits(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user credits information"""
        result = await db.fetchrow("""
            SELECT 
                u.user_id,
                u.name,
                u.email,
                COALESCE(c.credits, 0) as credits,
                c.last_updated
            FROM users u
            LEFT JOIN credits c ON u.user_id = c.user_id
            WHERE u.user_id = $1
        """, user_id)
        
        return dict(result) if result else None
    
    async def add_credits(self, user_id: int, amount: int) -> Dict[str, Any]:
        """Add credits to user account"""
        result = await db.fetchrow("""
            INSERT INTO credits (user_id, credits, last_updated) 
            VALUES ($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                credits = credits.credits + $2,
                last_updated = CURRENT_TIMESTAMP
            RETURNING credits, last_updated
        """, user_id, amount)
        
        return dict(result)
    
    async def deduct_credits(self, user_id: int, amount: int) -> Dict[str, Any]:
        """Deduct credits from user account"""
        result = await db.fetchrow("""
            UPDATE credits 
            SET credits = credits - $2, last_updated = CURRENT_TIMESTAMP
            WHERE user_id = $1
            RETURNING credits, last_updated
        """, user_id, amount)
        
        return dict(result)
    
    async def reset_credits(self, user_id: int) -> Dict[str, Any]:
        """Reset user credits to zero"""
        result = await db.fetchrow("""
            INSERT INTO credits (user_id, credits, last_updated) 
            VALUES ($1, 0, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                credits = 0,
                last_updated = CURRENT_TIMESTAMP
            RETURNING credits, last_updated
        """, user_id)
        
        return dict(result)
    
    async def log_transaction(self, user_id: int, amount: int, transaction_type: str, description: str = "") -> None:
        """Log credit transaction to audit trail"""
        try:
            await db.execute(
                """INSERT INTO credit_transactions (user_id, amount, transaction_type, description) 
                   VALUES ($1, $2, $3, $4)""",
                user_id, amount, transaction_type, description
            )
        except Exception as e:
            logger.error(f"Error logging transaction: {e}")

# Global service instance
credit_service = CreditService()
