"""
Hero Model — SQLModel table definition.
"""

from sqlmodel import Field, SQLModel


class Hero(SQLModel, table=True):
    """A hero stored in the database."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=3)
    power: str = Field(min_length=3)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = Field(default= True)
    