"""
Auth Router — Registration, Login, and Current User

Endpoints:
    POST /auth/register - Create new user
    POST /auth/login   - Login and get JWT token
    GET  /auth/me      - Get current authenticated user
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session
from typing import Annotated

from app.db import get_session
from app.dependencies import SessionDep, CurrentUser
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserOut
from app.security import create_access_token, verify_password, hash_password


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """
    OAuth2 password flow login.
    Validates credentials and returns {access_token, token_type}.
    Use the Swagger "Authorize" button to try it interactively.
    """
    user = session.exec(
        select(User).where(User.username == form.username)
    ).first()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(str(user.id))
    
    return Token(access_token=access_token, token_type="bearer")

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate, session: SessionDep
) -> UserOut:
    """
    Register a new user.
    
    - Username must be unique
    - Password is hashed before storage
    - New users are NOT admins by default
    """
    existing_user = session.exec(
        select(User).where(User.username == user_data.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        hashed_password=hashed_password,
        is_admin=False
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.get("/me", response_model=UserOut)
def get_current_user(current_user: CurrentUser) -> UserOut:
    """
    Get the currently authenticated user.
    
    Requires a valid JWT token in the Authorization header.
    """
    return current_user

