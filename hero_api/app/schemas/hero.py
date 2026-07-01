"""
Hero Schemas — Pydantic models for request/response contracts.

Separate from the SQLModel table so that:
  - HeroCreate: controls what the client sends
  - HeroUpdate: allows partial updates
  - AdminHeroCreate: what the admin sends
  - AdminHeroUpdate: what the admin updates
  - HeroOut:    controls what the API returns
"""

from pydantic import BaseModel, Field
from typing import Optional

class HeroCreate(BaseModel):
    """Schema for creating a new hero(POST /heroes)."""
    name: str = Field(min_length=3, max_length=30)
    power: str = Field(min_length=3, max_length=30)
    # level: int | None = Field(default=1, ge=1, le=100) 
    # active: bool = Field(default=True)

class HeroUpdate(BaseModel):
    """Schema for partial hero updates. All fields optional. (PATCH /heroes/{hero_id})"""
    name: Optional[str] = Field(default=None, min_length=3, max_length=30)
    power: Optional[str] = Field(default=None, min_length=3, max_length=30)
    # level: Optional[str] = Field(default=None, ge=1, le=100) 

class AdminHeroCreate(BaseModel):
    """Schema for creating a new hero by the admin(POST /heroes)."""
    name: str = Field(min_length=3, max_length=30)
    power: str = Field(min_length=3, max_length=30)
    level: int | None = Field(default=1, ge=1, le=100) 
    active: bool = Field(default=True)

class AdminHeroUpdate(BaseModel):
    """Schema for partial hero updates by the admin. All fields optional. (PATCH /heroes/{hero_id})"""
    name: Optional[str] = Field(default=None, min_length=3, max_length=30)
    power: Optional[str] = Field(default=None, min_length=3, max_length=30)
    level: Optional[int] = Field(default=None, ge=1, le=100)
    active: Optional[bool] = Field(default=True) 

class HeroOut(BaseModel):
    """Schema for hero responses. Used for GET /heroes and GET /heroes/{hero_id}"""
    id: int
    name: str
    power: str
    level: int | None = None
    active: bool = True

    class Config:
        from_attributes = True