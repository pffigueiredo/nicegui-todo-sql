from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class TodoItem(SQLModel, table=True):
    """Persistent todo item model stored in database"""

    __tablename__ = "todo_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=500)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)


class TodoItemCreate(SQLModel, table=False):
    """Schema for creating new todo items"""

    description: str = Field(max_length=500)


class TodoItemUpdate(SQLModel, table=False):
    """Schema for updating todo items"""

    description: Optional[str] = Field(default=None, max_length=500)
    completed: Optional[bool] = Field(default=None)
