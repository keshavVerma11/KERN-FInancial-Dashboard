"""
Reports API routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import get_current_user
from app.models.models import Transaction, Category
from typing import Optional
from datetime import date

router = APIRouter()


@router.get("/income-statement")
async def get_income_statement(
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate income statement (P&L) for a date range
    """
    from sqlalchemy import func
    
    # Query transactions in date range
    transactions = db.query(Transaction).filter(
        Transaction.organization_id == user["user_id"],
        Transaction.date >= start_date,
        Transaction.date <= end_date,
        Transaction.is_transfer == False  # Exclude internal transfers
    ).all()
    
    # Calculate totals by category type
    # TODO: Implement proper categorization with revenue vs expense
    total_revenue = sum(t.amount for t in transactions if t.amount > 0)
    total_expenses = sum(abs(t.amount) for t in transactions if t.amount < 0)
    net_income = total_revenue - total_expenses
    
    return {
        "report_type": "income_statement",
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "revenue": {
            "total": total_revenue,
            "categories": []  # TODO: Break down by category
        },
        "expenses": {
            "total": total_expenses,
            "categories": []  # TODO: Break down by category
        },
        "net_income": net_income,
        "transaction_count": len(transactions)
    }


@router.get("/balance-sheet")
async def get_balance_sheet(
    as_of_date: date = Query(..., description="Balance sheet as of this date"),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate balance sheet as of a specific date
    TODO: Implement full balance sheet logic
    """
    return {
        "report_type": "balance_sheet",
        "as_of_date": as_of_date,
        "assets": {
            "current_assets": {},
            "fixed_assets": {},
            "total": 0
        },
        "liabilities": {
            "current_liabilities": {},
            "long_term_liabilities": {},
            "total": 0
        },
        "equity": {
            "total": 0
        },
        "message": "Balance sheet generation coming soon"
    }


@router.get("/cash-flow")
async def get_cash_flow(
    start_date: date = Query(...),
    end_date: date = Query(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate cash flow statement
    TODO: Implement cash flow statement logic
    """
    return {
        "report_type": "cash_flow",
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "operating_activities": {},
        "investing_activities": {},
        "financing_activities": {},
        "message": "Cash flow statement generation coming soon"
    }
