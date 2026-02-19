"""Phase V — Direct migration script for Neon PostgreSQL."""
from app.database import engine
from sqlalchemy import text, inspect

def run():
    with engine.connect() as conn:
        insp = inspect(conn)
        cols = [c["name"] for c in insp.get_columns("tasks")]
        print("Existing columns:", cols)

        new_cols = {
            "tags": "VARCHAR(500)",
            "due_date": "TIMESTAMP",
            "reminder_at": "TIMESTAMP",
            "recurring_pattern": "VARCHAR(50)",
        }
        for col_name, col_type in new_cols.items():
            if col_name not in cols:
                conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_type}"))
                print(f"Added column: {col_name}")
            else:
                print(f"Column already exists: {col_name}")

        conn.execute(text("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL"))
        conn.commit()

        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_due_date ON tasks (due_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tasks_priority ON tasks (priority)"))
        conn.commit()
        print("Indexes ensured.")
        print("Phase V migration complete!")

if __name__ == "__main__":
    run()
