"""
Authentication API routes
"""
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from typing import Dict

router = APIRouter()


@router.get("/verify")
async def verify_auth(user: Dict = Depends(get_current_user)):
    """
    Verify authentication token
    Returns current user information
    """
    return {
        "authenticated": True,
        "user_id": user["user_id"],
        "email": user.get("email"),
        "role": user.get("role")
    }


@router.get("/me")
async def get_current_user_info(user: Dict = Depends(get_current_user)):
    """
    Get detailed information about current user
    """
    return {
        "user_id": user["user_id"],
        "email": user.get("email"),
        "role": user.get("role"),
        "metadata": user.get("payload", {}).get("user_metadata", {})
    }
