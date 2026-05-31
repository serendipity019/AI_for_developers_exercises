"""
Mission Schemas — Pydantic models for request/response contracts.

Separate from the SQLModel table so that:
  - MissionCreate: controls what the client sends
  - MissionUpdate: control what the client update
  - UserOut:    controls what the API returns
"""

from pydantic import BaseModel, Field
from typing import Optional

class MissionCreate(BaseModel):
    """Schema for creating a new Mission(POST /Missions)."""
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = Field(default= False)
    hero_id: int  # must reference existing hero

class MissionUpdate(BaseModel):
    """Used for PATCH /missions/{mission_id} - all fields optional."""
    title: Optional[str] = Field(default=None, min_length=5)
    difficulty: Optional[int] = Field(default=None ,ge=1, le=10)
    completed: Optional[bool] = Field(default= None)
    hero_id: Optional[int] = Field(default=None) 

class MissionOut(BaseModel):
    """Schema for missions responses. Used for GET /missions and GET /missions/{mission_id}"""
    id: int
    title: str 
    difficulty: int
    completed: bool
    hero_id: int  

    class Config:
        from_attributes = True