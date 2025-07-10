import pytest
from app.database import reset_db
from app.todo_service import (
    create_todo,
    get_all_todos,
    get_todo_by_id,
    update_todo,
    toggle_todo_completion,
    delete_todo,
    get_todo_stats,
)
from app.models import TodoItemCreate, TodoItemUpdate


@pytest.fixture()
def new_db():
    reset_db()
    yield
    reset_db()


def test_create_todo(new_db):
    """Test creating a new todo item"""
    todo_data = TodoItemCreate(description="Test todo item")
    todo = create_todo(todo_data)

    assert todo.id is not None
    assert todo.description == "Test todo item"
    assert todo.completed is False
    assert todo.created_at is not None
    assert todo.updated_at is None


def test_create_todo_with_long_description(new_db):
    """Test creating a todo with maximum length description"""
    long_description = "a" * 500
    todo_data = TodoItemCreate(description=long_description)
    todo = create_todo(todo_data)

    assert todo.description == long_description
    assert len(todo.description) == 500


def test_get_all_todos_empty(new_db):
    """Test getting all todos when none exist"""
    todos = get_all_todos()
    assert todos == []


def test_get_all_todos_with_items(new_db):
    """Test getting all todos with items"""
    # Create multiple todos
    todo1 = create_todo(TodoItemCreate(description="First todo"))
    todo2 = create_todo(TodoItemCreate(description="Second todo"))

    todos = get_all_todos()
    assert len(todos) == 2

    # Should be ordered by creation date desc (newest first)
    assert todos[0].id == todo2.id
    assert todos[1].id == todo1.id


def test_get_todo_by_id_exists(new_db):
    """Test getting a todo by ID when it exists"""
    todo = create_todo(TodoItemCreate(description="Test todo"))

    if todo.id is not None:
        retrieved = get_todo_by_id(todo.id)
        assert retrieved is not None
        assert retrieved.id == todo.id
        assert retrieved.description == "Test todo"


def test_get_todo_by_id_not_exists(new_db):
    """Test getting a todo by ID when it doesn't exist"""
    retrieved = get_todo_by_id(999)
    assert retrieved is None


def test_update_todo_description(new_db):
    """Test updating todo description"""
    todo = create_todo(TodoItemCreate(description="Original description"))

    if todo.id is not None:
        update_data = TodoItemUpdate(description="Updated description")
        updated = update_todo(todo.id, update_data)

        assert updated is not None
        assert updated.description == "Updated description"
        assert updated.completed is False  # Should remain unchanged
        assert updated.updated_at is not None


def test_update_todo_completion(new_db):
    """Test updating todo completion status"""
    todo = create_todo(TodoItemCreate(description="Test todo"))

    if todo.id is not None:
        update_data = TodoItemUpdate(completed=True)
        updated = update_todo(todo.id, update_data)

        assert updated is not None
        assert updated.completed is True
        assert updated.description == "Test todo"  # Should remain unchanged
        assert updated.updated_at is not None


def test_update_todo_both_fields(new_db):
    """Test updating both description and completion"""
    todo = create_todo(TodoItemCreate(description="Original"))

    if todo.id is not None:
        update_data = TodoItemUpdate(description="Updated", completed=True)
        updated = update_todo(todo.id, update_data)

        assert updated is not None
        assert updated.description == "Updated"
        assert updated.completed is True
        assert updated.updated_at is not None


def test_update_todo_not_exists(new_db):
    """Test updating a non-existent todo"""
    update_data = TodoItemUpdate(description="Updated")
    updated = update_todo(999, update_data)
    assert updated is None


def test_toggle_todo_completion_false_to_true(new_db):
    """Test toggling completion from false to true"""
    todo = create_todo(TodoItemCreate(description="Test todo"))

    if todo.id is not None:
        toggled = toggle_todo_completion(todo.id)

        assert toggled is not None
        assert toggled.completed is True
        assert toggled.updated_at is not None


def test_toggle_todo_completion_true_to_false(new_db):
    """Test toggling completion from true to false"""
    todo = create_todo(TodoItemCreate(description="Test todo"))

    if todo.id is not None:
        # First toggle to true
        toggle_todo_completion(todo.id)

        # Then toggle back to false
        toggled = toggle_todo_completion(todo.id)

        assert toggled is not None
        assert toggled.completed is False
        assert toggled.updated_at is not None


def test_toggle_todo_completion_not_exists(new_db):
    """Test toggling completion on non-existent todo"""
    toggled = toggle_todo_completion(999)
    assert toggled is None


def test_delete_todo_exists(new_db):
    """Test deleting an existing todo"""
    todo = create_todo(TodoItemCreate(description="To be deleted"))

    if todo.id is not None:
        result = delete_todo(todo.id)
        assert result is True

        # Verify it's actually deleted
        retrieved = get_todo_by_id(todo.id)
        assert retrieved is None


def test_delete_todo_not_exists(new_db):
    """Test deleting a non-existent todo"""
    result = delete_todo(999)
    assert result is False


def test_get_todo_stats_empty(new_db):
    """Test getting stats when no todos exist"""
    stats = get_todo_stats()

    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["pending"] == 0
    assert stats["completion_rate"] == 0


def test_get_todo_stats_with_todos(new_db):
    """Test getting stats with mixed todo statuses"""
    # Create todos with different completion statuses
    todo1 = create_todo(TodoItemCreate(description="Todo 1"))
    todo2 = create_todo(TodoItemCreate(description="Todo 2"))
    create_todo(TodoItemCreate(description="Todo 3"))

    # Complete some todos
    if todo1.id is not None:
        toggle_todo_completion(todo1.id)
    if todo2.id is not None:
        toggle_todo_completion(todo2.id)

    stats = get_todo_stats()

    assert stats["total"] == 3
    assert stats["completed"] == 2
    assert stats["pending"] == 1
    assert stats["completion_rate"] == 66.7


def test_get_todo_stats_all_completed(new_db):
    """Test getting stats when all todos are completed"""
    todo1 = create_todo(TodoItemCreate(description="Todo 1"))
    todo2 = create_todo(TodoItemCreate(description="Todo 2"))

    # Complete all todos
    if todo1.id is not None:
        toggle_todo_completion(todo1.id)
    if todo2.id is not None:
        toggle_todo_completion(todo2.id)

    stats = get_todo_stats()

    assert stats["total"] == 2
    assert stats["completed"] == 2
    assert stats["pending"] == 0
    assert stats["completion_rate"] == 100.0


def test_todo_ordering_by_creation_date(new_db):
    """Test that todos are ordered by creation date (newest first)"""
    # Create todos with slight delays to ensure different timestamps
    todo1 = create_todo(TodoItemCreate(description="First todo"))
    todo2 = create_todo(TodoItemCreate(description="Second todo"))
    todo3 = create_todo(TodoItemCreate(description="Third todo"))

    todos = get_all_todos()

    # Should be ordered newest first
    assert todos[0].id == todo3.id
    assert todos[1].id == todo2.id
    assert todos[2].id == todo1.id


def test_todo_timestamps(new_db):
    """Test that todo timestamps are handled correctly"""
    todo = create_todo(TodoItemCreate(description="Test todo"))

    assert todo.created_at is not None
    assert todo.updated_at is None

    # Update the todo
    if todo.id is not None:
        updated = update_todo(todo.id, TodoItemUpdate(description="Updated"))

        assert updated is not None
        assert updated.created_at == todo.created_at  # Should not change
        assert updated.updated_at is not None  # Should be set
        assert updated.updated_at > todo.created_at  # Should be more recent
