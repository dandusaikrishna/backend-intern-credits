"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class CreditAmount(BaseModel):
    amount: int = Field(..., gt=0, description="Amount must be a positive integer")

class UserCreditsResponse(BaseModel):
    user_id: int
    name: str
    email: str
    credits: int
    last_updated: Optional[datetime]

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class SchemaColumn(BaseModel):
    name: str
    type: str
    constraints: Optional[str] = None

class SchemaUpdateRequest(BaseModel):
    operation: str = Field(..., description="Operation type: add_column, drop_column, add_index")
    table: str = Field(..., description="Table name")
    columns: List[SchemaColumn] = Field(..., description="List of columns")

class TransactionLog(BaseModel):
    transaction_id: int
    user_id: int
    amount: int
    transaction_type: str
    description: Optional[str]
    created_at: datetime
