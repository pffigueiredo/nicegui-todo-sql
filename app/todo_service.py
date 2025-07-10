from typing import List, Optional
from datetime import datetime
from sqlmodel import select, desc
from app.database import get_session
from app.models import TodoItem, TodoItemCreate, TodoItemUpdate


def create_todo(todo_data: TodoItemCreate) -> TodoItem:
    """Create a new todo item"""
    with get_session() as session:
        todo = TodoItem(description=todo_data.description)
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


def get_all_todos() -> List[TodoItem]:
    """Get all todo items ordered by creation date"""
    with get_session() as session:
        statement = select(TodoItem).order_by(desc(TodoItem.created_at))
        todos = session.exec(statement).all()
        return list(todos)


def get_todo_by_id(todo_id: int) -> Optional[TodoItem]:
    """Get a specific todo item by ID"""
    with get_session() as session:
        return session.get(TodoItem, todo_id)


def update_todo(todo_id: int, update_data: TodoItemUpdate) -> Optional[TodoItem]:
    """Update a todo item"""
    with get_session() as session:
        todo = session.get(TodoItem, todo_id)
        if todo is None:
            return None

        if update_data.description is not None:
            todo.description = update_data.description
        if update_data.completed is not None:
            todo.completed = update_data.completed

        todo.updated_at = datetime.utcnow()
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


def toggle_todo_completion(todo_id: int) -> Optional[TodoItem]:
    """Toggle the completion status of a todo item"""
    with get_session() as session:
        todo = session.get(TodoItem, todo_id)
        if todo is None:
            return None

        todo.completed = not todo.completed
        todo.updated_at = datetime.utcnow()
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


def delete_todo(todo_id: int) -> bool:
    """Delete a todo item"""
    with get_session() as session:
        todo = session.get(TodoItem, todo_id)
        if todo is None:
            return False

        session.delete(todo)
        session.commit()
        return True


def get_todo_stats() -> dict:
    """Get statistics about todos"""
    todos = get_all_todos()
    total = len(todos)
    completed = sum(1 for todo in todos if todo.completed)
    pending = total - completed

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 1),
    }
