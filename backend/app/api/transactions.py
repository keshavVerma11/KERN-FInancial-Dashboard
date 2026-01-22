"""
Transactions API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.models import Transaction, TransactionStatus
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID

router = APIRouter()


# Pydantic schemas for request/response
class TransactionCreate(BaseModel):
    date: date
    amount: float
    description: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[UUID] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    merchant: Optional[str] = None
    category_id: Optional[UUID] = None
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None
    is_transfer: Optional[bool] = None
    is_owner_draw: Optional[bool] = None


class TransactionResponse(BaseModel):
    id: UUID
    date: date
    amount: float
    description: Optional[str]
    merchant: Optional[str]
    category_id: Optional[UUID]
    confidence_score: Optional[float]
    status: TransactionStatus
    notes: Optional[str]
    payment_method: Optional[str]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[TransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TransactionStatus] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all transactions for the current user's organization
    """
    query = db.query(Transaction).filter(
        Transaction.organization_id == user["user_id"]
    )
    
    # Apply filters
    if status:
        query = query.filter(Transaction.status == status)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Order by date descending
    query = query.order_by(Transaction.date.desc())
    
    transactions = query.offset(skip).limit(limit).all()
    return transactions


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    transaction: TransactionCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transaction
    """
    db_transaction = Transaction(
        organization_id=user["user_id"],
        **transaction.model_dump()
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    return db_transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a single transaction by ID
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.organization_id == user["user_id"]
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a transaction
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.organization_id == user["user_id"]
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Update fields
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    db.commit()
    db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: UUID,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction
    """
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.organization_id == user["user_id"]
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}


@router.get("/stats/summary")
async def get_transaction_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get transaction summary statistics including income/expense breakdown
    """
    from sqlalchemy import func, case

    query = db.query(Transaction).filter(
        Transaction.organization_id == user["user_id"]
    )

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    total_transactions = query.count()

    # Calculate income (positive amounts) and expenses (negative amounts)
    income_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.organization_id == user["user_id"],
        Transaction.amount > 0
    )
    expense_query = db.query(func.sum(Transaction.amount)).filter(
        Transaction.organization_id == user["user_id"],
        Transaction.amount < 0
    )

    if start_date:
        income_query = income_query.filter(Transaction.date >= start_date)
        expense_query = expense_query.filter(Transaction.date >= start_date)
    if end_date:
        income_query = income_query.filter(Transaction.date <= end_date)
        expense_query = expense_query.filter(Transaction.date <= end_date)

    total_income = income_query.scalar() or 0
    total_expenses = abs(expense_query.scalar() or 0)
    net_amount = float(total_income) - float(total_expenses)

    pending_count = query.filter(Transaction.status == TransactionStatus.PENDING).count()

    return {
        "total_transactions": total_transactions,
        "total_income": float(total_income),
        "total_expenses": float(total_expenses),
        "net_amount": net_amount,
        "pending_review": pending_count,
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }
