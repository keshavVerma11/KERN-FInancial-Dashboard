"""
Authentication utilities and dependencies
"""
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from typing import Dict

security = HTTPBearer()


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> Dict:
    """
    Verify Supabase JWT token and return user payload
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        
    Returns:
        Dict containing user information (sub, email, etc.)
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_aud": True}
        )
        
        # Extract user info
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
            
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "role": payload.get("role"),
            "payload": payload
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Dependency to get current user
async def get_current_user(
    user_data: Dict = Depends(verify_token)
) -> Dict:
    """
    Get current authenticated user
    Use this as a dependency in your routes
    """
    return user_data


# Optional: Admin role check
async def require_admin(
    user_data: Dict = Depends(get_current_user)
) -> Dict:
    """
    Require user to have admin role
    """
    if user_data.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user_data
