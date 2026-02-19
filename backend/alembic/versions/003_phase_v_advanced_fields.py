"""Phase V — Add advanced task fields (tags, due_date, reminder_at, recurring_pattern)

Revision ID: 003
Revises: 002
Create Date: 2026-02-17 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("tags", sa.String(length=500), nullable=True))
    op.add_column("tasks", sa.Column("due_date", sa.DateTime(), nullable=True))
    op.add_column("tasks", sa.Column("reminder_at", sa.DateTime(), nullable=True))
    op.add_column("tasks", sa.Column("recurring_pattern", sa.String(length=50), nullable=True))

    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    op.create_index("ix_tasks_priority", "tasks", ["priority"])

    op.execute("UPDATE tasks SET priority = 'medium' WHERE priority IS NULL")


def downgrade():
    op.drop_index("ix_tasks_priority", table_name="tasks")
    op.drop_index("ix_tasks_due_date", table_name="tasks")
    op.drop_column("tasks", "recurring_pattern")
    op.drop_column("tasks", "reminder_at")
    op.drop_column("tasks", "due_date")
    op.drop_column("tasks", "tags")
