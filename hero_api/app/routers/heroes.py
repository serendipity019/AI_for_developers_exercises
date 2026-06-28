"""
Heroes Router — CRUD operations for heroes

Endpoints:
    POST   /heroes           - Create hero (authenticated)
    GET    /heroes           - List all heroes (public)
    GET    /heroes/{hero_id}      - Get hero by ID (public)
    PATCH  /heroes/{hero_id}      - Update hero (authenticated)
    DELETE /heroes/{hero_id}      - Delete hero (admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import Annotated

from app.db import get_session
from app.dependencies import CurrentAdmin, CurrentUser, SessionDep
from app.models.hero import Hero
from app.models.mission import Mission
from app.schemas.hero import (
    HeroCreate,
    HeroUpdate,
    AdminHeroCreate,
    AdminHeroUpdate,
    HeroOut
) 

router = APIRouter(prefix="/heroes", tags=["Heroes"])


@router.post("/", response_model=HeroOut, status_code=status.HTTP_201_CREATED)
def create_hero(hero_data: HeroCreate | AdminHeroCreate, session: SessionDep, user: CurrentUser) -> HeroOut:
    """Create a new hero. Requires authentication.
        - Normal users: only name and power (level=1, active=True forced)
        - Admins: can set level and active status
    """
    hero_dict = hero_data.model_dump()

    if not user.is_admin:
        hero_dict["level"] = 1
        hero_dict["active"] = True

    hero = Hero(**hero_dict)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@router.patch("/{hero_id}", response_model=HeroOut)
def update_hero(hero_id: int, updated_data: HeroUpdate | AdminHeroUpdate, session: SessionDep, user: CurrentUser) -> HeroOut:
    """
    Partial update: only provided fields are changed.
    Requires authentication.

    - Normal users: can only update name and power
    - Admins: can update name, power, level, and active status
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hero not found"
        )
    
    hero_dict = updated_data.model_dump(exclude_unset=True)

    if not user.is_admin:
        hero_dict.pop("level", None)
        hero_dict.pop("active", None)
    
    for field, value in hero_dict.items():
        setattr(hero, field, value)  
    
    session.commit()
    session.refresh(hero)
    return hero

@router.get("/", response_model=list[HeroOut])
def list_heroes(session: SessionDep, active_only: bool = False, skip: int = 0, limit: int = 20) -> list[HeroOut]:
    """
    Get all heroes.
    
    - Public endpoint (no authentication required)
    - Optional filter: active_only=true
    """
    query = select(Hero)

    if active_only:
        query = query.where(Hero.active == True)

    heroes = session.exec(query.offset(skip).limit(limit)).all()
    return heroes


@router.get("/{hero_id}", response_model=HeroOut)
def get_hero(hero_id: int ,session: SessionDep) -> HeroOut:
    """Get a single hero by ID."""
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )
    return hero

@router.delete("/{hero_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hero(hero_id: int, session: SessionDep, user: CurrentAdmin):
    """Delete hero by id. 
       - Only admin can delete heroes.
       - Cannot delete hero with active missions
    """
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found"
        )
    
    # Check if hero has active missions
    active_missions = session.exec(
        select(Mission).where(
            Mission.hero_id == hero_id,
            Mission.completed == False
        )
    ).first()

    if active_missions: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete hero with incomplete missions"
        )

    session.delete(hero)
    session.commit()
    


