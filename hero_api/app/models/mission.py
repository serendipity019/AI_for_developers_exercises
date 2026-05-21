"""
Mission Model — SQLModel table definition.
"""

from sqlmodel import Field, SQLModel

class Mission(SQLModel, table=True):
    """A mission stored in the database. Has foreign key to Hero """
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = Field(default= False)
    hero_id: int = Field(foreign_key="hero.id")