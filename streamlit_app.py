"""
Streamlit Todo App - A fully functional Todo application with user authentication.
Deploy for free on Streamlit Cloud (https://streamlit.io/cloud)

Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any

# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Todo App",
    page_icon="✅",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Database path - use absolute path for Streamlit Cloud compatibility
if os.path.exists("/mount/src"):
    DB_PATH = "/mount/src/todo.db"
else:
    DB_PATH = "todo.db"

# =============================================================================
# DATABASE SETUP
# =============================================================================

def init_database():
    """Initialize the SQLite database with users and todos tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Create todos table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create index for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id)
    """)

    conn.commit()
    conn.close()


def get_db_connection():
    """Get a database connection with row factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# USER AUTHENTICATION
# =============================================================================

def hash_password(password: str) -> str:
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(password) == password_hash


def create_user(email: str, password: str) -> tuple[bool, str]:
    """
    Create a new user account.

    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (email.lower(),))
        if cursor.fetchone():
            return False, "An account with this email already exists"

        # Create user
        password_hash = hash_password(password)
        created_at = datetime.now().isoformat()

        cursor.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email.lower(), password_hash, created_at)
        )

        conn.commit()
        return True, "Account created successfully! Please log in."

    except Exception as e:
        return False, f"Error creating account: {str(e)}"
    finally:
        conn.close()


def authenticate_user(email: str, password: str) -> tuple[bool, str, int]:
    """
    Authenticate a user.

    Returns:
        tuple: (success: bool, message: str, user_id: int)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, email, password_hash FROM users WHERE email = ?",
            (email.lower(),)
        )
        user = cursor.fetchone()

        if not user:
            return False, "Invalid email or password", 0

        if not verify_password(password, user["password_hash"]):
            return False, "Invalid email or password", 0

        return True, "Login successful!", user["id"]

    except Exception as e:
        return False, f"Error during login: {str(e)}", 0
    finally:
        conn.close()


# =============================================================================
# TODO OPERATIONS
# =============================================================================

def create_todo(user_id: int, title: str, description: str = "") -> tuple[bool, str]:
    """Create a new todo for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO todos (user_id, title, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, description, now, now)
        )
        conn.commit()
        return True, "Todo created successfully!"
    except Exception as e:
        return False, f"Error creating todo: {str(e)}"
    finally:
        conn.close()


def get_user_todos(user_id: int, show_completed: bool = True) -> list[Dict[str, Any]]:
    """Get all todos for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if show_completed:
            cursor.execute(
                "SELECT * FROM todos WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
        else:
            cursor.execute(
                "SELECT * FROM todos WHERE user_id = ? AND completed = 0 ORDER BY created_at DESC",
                (user_id,)
            )

        todos = []
        for row in cursor.fetchall():
            todos.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "completed": bool(row["completed"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })

        return todos

    finally:
        conn.close()


def update_todo(todo_id: int, user_id: int, title: str, description: str) -> tuple[bool, str]:
    """Update a todo."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        now = datetime.now().isoformat()
        cursor.execute(
            "UPDATE todos SET title = ?, description = ?, updated_at = ? WHERE id = ? AND user_id = ?",
            (title, description, now, todo_id, user_id)
        )

        if cursor.rowcount == 0:
            return False, "Todo not found or access denied"

        conn.commit()
        return True, "Todo updated successfully!"

    except Exception as e:
        return False, f"Error updating todo: {str(e)}"
    finally:
        conn.close()


def toggle_todo(todo_id: int, user_id: int) -> tuple[bool, str]:
    """Toggle todo completion status."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get current status
        cursor.execute("SELECT completed FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id))
        result = cursor.fetchone()

        if not result:
            return False, "Todo not found or access denied"

        new_status = not bool(result["completed"])
        now = datetime.now().isoformat()

        cursor.execute(
            "UPDATE todos SET completed = ?, updated_at = ? WHERE id = ? AND user_id = ?",
            (new_status, now, todo_id, user_id)
        )

        conn.commit()
        status_text = "completed" if new_status else "uncompleted"
        return True, f"Todo marked as {status_text}"

    except Exception as e:
        return False, f"Error toggling todo: {str(e)}"
    finally:
        conn.close()


def delete_todo(todo_id: int, user_id: int) -> tuple[bool, str]:
    """Delete a todo."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM todos WHERE id = ? AND user_id = ?", (todo_id, user_id))

        if cursor.rowcount == 0:
            return False, "Todo not found or access denied"

        conn.commit()
        return True, "Todo deleted successfully!"

    except Exception as e:
        return False, f"Error deleting todo: {str(e)}"
    finally:
        conn.close()


# =============================================================================
# STREAMLIT UI - AUTH PAGES
# =============================================================================

def show_login_page():
    """Display the login page."""
    st.title("🔐 Login")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                success, message, user_id = authenticate_user(email, password)
                if success:
                    st.session_state["user_id"] = user_id
                    st.session_state["user_email"] = email
                    st.session_state["page"] = "todos"
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    st.markdown("Don't have an account? [Sign up](/?page=signup)")


def show_signup_page():
    """Display the signup page."""
    st.title("📝 Create Account")

    with st.form("signup_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password",
                                  help="At least 8 characters with uppercase, lowercase, number, and special character")
        password_confirm = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Create Account", use_container_width=True)

        if submit:
            if not email or not password or not password_confirm:
                st.error("Please fill in all fields")
            elif password != password_confirm:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters")
            else:
                success, message = create_user(email, password)
                if success:
                    st.success(message + " Please log in.")
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    st.markdown("Already have an account? [Login](/?page=login)")


# =============================================================================
# STREAMLIT UI - TODO PAGE
# =============================================================================

def show_todos_page():
    """Display the todos page."""
    # Header with logout
    col1, col2 = st.columns([1, 1])
    with col1:
        st.title("📋 My Todos")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown(f"**Logged in as:** {st.session_state.get('user_email', '')}")
    st.markdown("---")

    user_id = st.session_state["user_id"]

    # Add new todo form
    with st.expander("➕ Add New Todo", expanded=False):
        with st.form("add_todo_form"):
            title = st.text_input("Title", placeholder="What needs to be done?")
            description = st.text_area("Description (optional)", placeholder="Add details...")
            submit = st.form_submit_button("Add Todo", use_container_width=True)

            if submit:
                if not title:
                    st.error("Please enter a title")
                else:
                    success, message = create_todo(user_id, title, description)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)

    # Show completed toggle
    show_completed = st.checkbox("Show completed todos", value=True)

    # Get and display todos
    todos = get_user_todos(user_id, show_completed)

    if not todos:
        st.info("No todos yet! Add your first todo above.")
    else:
        # Stats
        total = len(todos)
        completed = sum(1 for t in todos if t["completed"])
        pending = total - completed

        col1, col2, col3 = st.columns(3)
        col1.metric("Total", total)
        col2.metric("Pending", pending)
        col3.metric("Completed", completed)

        st.markdown("---")

        # Display todos
        for todo in todos:
            with st.container():
                col1, col2, col3 = st.columns([6, 1, 1])

                # Todo content
                with col1:
                    if todo["completed"]:
                        st.markdown(f"~~**{todo['title']}**~~")
                        if todo["description"]:
                            st.caption(f"~~{todo['description']}~~")
                    else:
                        st.markdown(f"**{todo['title']}**")
                        if todo["description"]:
                            st.caption(todo["description"])
                    st.caption(f"Created: {todo['created_at'][:10]}")

                # Toggle button
                with col2:
                    if st.button("✓" if not todo["completed"] else "○",
                                key=f"toggle_{todo['id']}",
                                help="Toggle completion"):
                        success, message = toggle_todo(todo["id"], user_id)
                        if success:
                            st.rerun()
                        else:
                            st.error(message)

                # Delete button
                with col3:
                    if st.button("🗑️", key=f"delete_{todo['id']}", help="Delete todo"):
                        success, message = delete_todo(todo["id"], user_id)
                        if success:
                            st.rerun()
                        else:
                            st.error(message)

                st.markdown("---")


# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main application entry point."""
    # Initialize database on app start
    init_database()

    # Get query params to handle navigation
    query_params = st.query_params
    requested_page = query_params.get("page", "")

    # Session state initialization
    if "page" not in st.session_state:
        st.session_state["page"] = requested_page if requested_page else "login"

    # Auto-login check (restore session if available)
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None
    if "user_email" not in st.session_state:
        st.session_state["user_email"] = None

    # Page routing
    page = st.session_state.get("page", "login")

    # Auto-redirect if logged in
    if st.session_state["user_id"] and page in ["login", "signup"]:
        page = "todos"
        st.session_state["page"] = "todos"

    # Show appropriate page
    if st.session_state["user_id"] and page == "todos":
        show_todos_page()
    elif page == "signup":
        show_signup_page()
    else:
        show_login_page()


if __name__ == "__main__":
    main()
