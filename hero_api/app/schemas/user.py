"""
User Schemas — Pydantic models for request/response contracts.

Separate from the SQLModel table so that:
  - UserCreate: controls what the client sends
  - UserOut:    controls what the API returns
"""

from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    """Used for POST /auth/login"""
    username: str 
    password: str

class UserOut(BaseModel):
    """Schema for user responses (password excluded). Used for GET /users and GET /users/{user_id}"""
    id: int
    username: str
    is_admin: bool

    class Config:
        from_attributes = True