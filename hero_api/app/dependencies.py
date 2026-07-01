import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from typing import Annotated

from app.db import get_session
from app.config import get_settings
from app.models.user import User
from app.schemas.auth import TokenPayload

settings = get_settings()

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"auth/login"
)

SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]

def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="User not found")
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]

def get_current_admin(current_user: CurrentUser) -> User:
    """Get current user and verify they are an admin."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

CurrentAdmin = Annotated[User, Depends(get_current_admin)]