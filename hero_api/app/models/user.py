"""
User Model — SQLModel table definition.
"""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """A user stored in the database."""
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=30)
    hashed_password: str
    is_admin: bool = Field(default=False)