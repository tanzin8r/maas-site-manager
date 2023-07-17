from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)


class User(BaseModel):
    """A user."""

    id: int
    email: EmailStr = Field(title="email@example.com")
    username: str
    full_name: str
    is_admin: bool


class UserCreate(BaseModel):
    """Creating a new user"""

    email: str
    username: str
    full_name: str
    password: str
    is_admin: bool


class UserUpdate(BaseModel):
    """User updatable fields"""

    username: str | None = None
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    is_admin: bool | None = None
