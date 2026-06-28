"""
Missions Router — CRUD operations for missions

Endpoints:
    POST   /missions           - Create mission (authenticated)
    GET    /missions           - List all missions (public)
    GET    /missions/{mission_id}      - Get mission by ID (public)
    PATCH  /missions/{mission_id}      - Update mission (authenticated)
    DELETE /missions/{mission_id}      - Delete mission (admin only)
"""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.db import get_session
from app.dependencies import CurrentAdmin, CurrentUser, SessionDep
from app.models.hero import Hero
from app.models.mission import Mission
from app.schemas.mission import (
    MissionCreate,
    MissionUpdate,
    MissionOut
)

router = APIRouter(prefix="/missions", tags=["Missions"])

@router.post("/", response_model=MissionOut, status_code=status.HTTP_201_CREATED)
def create_mission(mission_data: MissionCreate, session: SessionDep, user: CurrentUser) -> MissionOut:
    """ Create a new mission for a hero. 
        - Requires authentication
        - hero_id must exist
    """

    mission_dict = mission_data.model_dump()

    hero = session.get(Hero, mission_dict.hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found"
        )
    
    mission = Mission(**mission_dict)
    session.add(mission)
    session.commit()
    session.refresh(mission)
    return mission

@router.patch("/{mission_id}", response_model=MissionOut)
def update_mission(mission_id: int, update_data: MissionUpdate, session: SessionDep, user: CurrentUser) -> MissionOut:
    """ Partial update: only provided fields are changed.
        - Requires authentication.
        - If hero_id is updated, new hero must exist
    """

    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    mission_dict = update_data.model_dump(exclude_unset=True)

    if "hero_id" in mission_dict and mission_dict.hero_id is not None:
        hero = session.get(Hero, mission_dict.hero_id)
        if not hero:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hero not found"
            )

    for field, value in mission_dict.items():
        setattr(mission, field, value)
    
    session.commit()
    session.refresh(mission)
    return mission

@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mission(mission_id: int, session: SessionDep, user: CurrentAdmin) -> None:
    """
    Delete mission by id. 
       - Only admin can delete missions.
    """

    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    session.delete(mission)
    session.commit()

@router.get("/", response_model=list[MissionOut])
def get_missions(session: SessionDep, completed: bool | None = None, skip: int = 0, limit: int = 20) -> list[MissionOut]:
    """
    Get all missions.    
    - Public endpoint (no authentication required)
    - Optional filter: completed=true/false
    """
    query = select(Mission)

    if completed is not None:
        query = query.where(Mission.completed == completed)

    missions = session.exec(query.offset(skip).limit(limit)).all()
    return missions

@router.get("/{mission_id}", response_model=MissionOut)
def get_mission(mission_id: int, session: SessionDep) -> MissionOut:
    """Get a single mission by ID."""

    mission = session.get(Mission, mission_id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found"
        )
    
    return mission
