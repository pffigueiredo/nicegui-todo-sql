from nicegui import ui
from app.todo_service import create_todo, get_all_todos, toggle_todo_completion, delete_todo, get_todo_stats
from app.models import TodoItemCreate, TodoItem


# Modern color theme
def apply_modern_theme():
    ui.colors(
        primary="#3b82f6",  # Blue
        secondary="#64748b",  # Gray
        accent="#10b981",  # Green
        positive="#10b981",  # Success green
        negative="#ef4444",  # Red
        warning="#f59e0b",  # Amber
        info="#3b82f6",  # Blue
    )


def create_metric_card(title: str, value: str, icon: str, color: str = "primary"):
    """Create a metric card component"""
    with ui.card().classes("p-6 bg-white shadow-lg rounded-xl hover:shadow-xl transition-shadow min-w-32"):
        with ui.row().classes("items-center gap-4"):
            ui.icon(icon).classes(f"text-{color} text-2xl")
            with ui.column().classes("gap-1"):
                ui.label(value).classes("text-2xl font-bold text-gray-800")
                ui.label(title).classes("text-sm text-gray-500 uppercase tracking-wider")


def create_todo_item_card(todo: TodoItem, on_change_callback):
    """Create a todo item card component"""
    with ui.card().classes("w-full p-4 shadow-md rounded-lg hover:shadow-lg transition-shadow"):
        with ui.row().classes("items-center gap-4 w-full"):
            # Checkbox for completion status
            checkbox = ui.checkbox(value=todo.completed).classes("text-lg")

            # Todo description
            description_classes = "flex-1 text-gray-800"
            if todo.completed:
                description_classes += " line-through text-gray-400"

            ui.label(todo.description).classes(description_classes)

            # Created date
            created_date = todo.created_at.strftime("%b %d, %Y")
            ui.label(created_date).classes("text-sm text-gray-500 min-w-fit")

            # Delete button
            ui.button(
                icon="delete", on_click=lambda e, todo_id=todo.id: delete_todo_item(todo_id, on_change_callback)
            ).classes("text-red-500 hover:bg-red-50").props("flat round size=sm")

            # Handle checkbox changes
            checkbox.on("update:model-value", lambda e, todo_id=todo.id: toggle_todo_item(todo_id, on_change_callback))


def delete_todo_item(todo_id: int | None, on_change_callback):
    """Delete a todo item with confirmation"""
    if todo_id is None:
        return

    success = delete_todo(todo_id)
    if success:
        ui.notify("Todo item deleted successfully!", type="positive")
        on_change_callback()
    else:
        ui.notify("Failed to delete todo item", type="negative")


def toggle_todo_item(todo_id: int | None, on_change_callback):
    """Toggle todo completion status"""
    if todo_id is None:
        return

    updated_todo = toggle_todo_completion(todo_id)
    if updated_todo:
        status = "completed" if updated_todo.completed else "reopened"
        ui.notify(f"Todo item {status}!", type="positive")
        on_change_callback()
    else:
        ui.notify("Failed to update todo item", type="negative")


def create():
    """Create the todo application UI"""
    apply_modern_theme()

    @ui.page("/")
    def todo_app():
        # Page title and styling
        ui.add_head_html("""
        <style>
            .todo-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
        </style>
        """)

        # Main container
        with ui.column().classes("todo-container"):
            # Header
            ui.label("✅ Todo Manager").classes("text-4xl font-bold text-gray-800 mb-2 text-center")
            ui.label("Organize your tasks efficiently").classes("text-lg text-gray-600 mb-8 text-center")

            # Stats cards container
            stats_container = ui.row().classes("gap-4 mb-8 justify-center")

            # Add todo form
            with ui.card().classes("glass-card p-6 shadow-lg rounded-xl mb-8"):
                ui.label("Add New Todo").classes("text-xl font-bold mb-4 text-gray-800")

                with ui.row().classes("gap-4 w-full items-end"):
                    new_todo_input = (
                        ui.input(placeholder="Enter your todo description...").classes("flex-1").props("outlined")
                    )

                    ui.button(
                        "Add Todo", icon="add", on_click=lambda: add_new_todo(new_todo_input, refresh_todos)
                    ).classes("bg-primary text-white px-6 py-3 rounded-lg shadow-md hover:shadow-lg")

                # Handle Enter key
                new_todo_input.on("keydown.enter", lambda: add_new_todo(new_todo_input, refresh_todos))

            # Todo list container
            todo_list_container = ui.column().classes("gap-4 w-full")

            def refresh_todos():
                """Refresh the todo list and stats"""
                # Clear current todos
                todo_list_container.clear()
                stats_container.clear()

                # Get updated data
                todos = get_all_todos()
                stats = get_todo_stats()

                # Update stats cards
                with stats_container:
                    create_metric_card("Total Tasks", str(stats["total"]), "task_alt", "primary")
                    create_metric_card("Completed", str(stats["completed"]), "check_circle", "positive")
                    create_metric_card("Pending", str(stats["pending"]), "pending", "warning")
                    create_metric_card("Progress", f"{stats['completion_rate']}%", "trending_up", "info")

                # Update todo list
                with todo_list_container:
                    if not todos:
                        with ui.card().classes("p-8 text-center bg-gray-50 rounded-lg"):
                            ui.icon("task_alt").classes("text-6xl text-gray-300 mb-4")
                            ui.label("No todos yet!").classes("text-xl text-gray-500 mb-2")
                            ui.label("Add your first todo above to get started.").classes("text-gray-400")
                    else:
                        ui.label(f"Your Tasks ({len(todos)})").classes("text-lg font-semibold text-gray-700 mb-4")

                        # Separate completed and pending todos
                        pending_todos = [todo for todo in todos if not todo.completed]
                        completed_todos = [todo for todo in todos if todo.completed]

                        # Show pending todos first
                        if pending_todos:
                            ui.label("Pending").classes("text-md font-medium text-gray-600 mb-2")
                            for todo in pending_todos:
                                create_todo_item_card(todo, refresh_todos)

                        # Show completed todos
                        if completed_todos:
                            ui.label("Completed").classes("text-md font-medium text-gray-600 mb-2 mt-6")
                            for todo in completed_todos:
                                create_todo_item_card(todo, refresh_todos)

            # Initial load
            refresh_todos()


def add_new_todo(input_field, refresh_callback):
    """Add a new todo item"""
    description = input_field.value.strip()

    if not description:
        ui.notify("Please enter a todo description", type="warning")
        return

    if len(description) > 500:
        ui.notify("Todo description is too long (max 500 characters)", type="warning")
        return

    try:
        todo_data = TodoItemCreate(description=description)
        create_todo(todo_data)
        input_field.set_value("")  # Clear the input
        ui.notify("Todo added successfully!", type="positive")
        refresh_callback()
    except Exception as e:
        ui.notify(f"Failed to add todo: {str(e)}", type="negative")
