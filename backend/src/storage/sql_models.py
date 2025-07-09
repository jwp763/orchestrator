from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
    Enum,
    JSON,
    Date,
    Float,
    Boolean,
)
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime

from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    priority = Column(Enum(ProjectPriority), default=ProjectPriority.MEDIUM)
    tags = Column(JSON, default=list)
    due_date = Column(Date)
    start_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=False)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)

    # Hierarchical fields
    parent_id = Column(String, ForeignKey("tasks.id"))
    estimated_minutes = Column(Integer)
    actual_minutes = Column(Integer)
    depth = Column(Integer, default=0)
    dependencies = Column(JSON, default=list)

    # Scheduling
    due_date = Column(Date)

    # Assignment
    assignee = Column(String)
    tags = Column(JSON, default=list)
    labels = Column(JSON, default=list)

    # Integration references
    motion_task_id = Column(String)
    linear_issue_id = Column(String)
    notion_task_id = Column(String)
    gitlab_issue_id = Column(String)

    # Metadata
    task_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(String, nullable=False)

    # Computed fields (these would be calculated dynamically, not stored)
    # is_overdue = Column(Boolean, default=False)
    # days_until_due = Column(Integer)

    project = relationship("Project", back_populates="tasks")
    parent = relationship("Task", remote_side=[id])
    children = relationship("Task")
