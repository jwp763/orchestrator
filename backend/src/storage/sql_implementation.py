"""SQL implementation of the storage interface."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from src.storage.interface import StorageInterface
from src.storage.sql_models import Base, Project as SQLProject, Task as SQLTask
from src.models import Project, Task, ProjectStatus, TaskStatus, ProjectPriority
from src.models.task import TaskPriority
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op


class SQLStorage(StorageInterface):
    """SQL implementation of the storage interface using SQLAlchemy."""

    def __init__(self, database_url: str = "sqlite:///orchestrator.db"):
        """Initialize the SQL storage with database URL."""
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._session: Optional[Session] = None

        # Create tables
        Base.metadata.create_all(bind=self.engine)

    @property
    def session(self) -> Session:
        """Get the current session, creating one if needed."""
        if self._session is None:
            self._session = self.SessionLocal()
        return self._session

    @session.setter
    def session(self, value: Session) -> None:
        """Set the session for testing purposes."""
        if self._session is not None:
            self._session.close()
        self._session = value

    def _convert_sql_project_to_pydantic(self, sql_project: SQLProject) -> Project:
        """Convert SQLAlchemy Project to Pydantic Project."""
        tasks = [self._convert_sql_task_to_pydantic(task) for task in sql_project.tasks]

        return Project(
            id=sql_project.id,
            name=sql_project.name,
            description=sql_project.description,
            status=sql_project.status,
            priority=sql_project.priority,
            tags=sql_project.tags or [],
            due_date=sql_project.due_date,
            start_date=sql_project.start_date,
            created_at=sql_project.created_at,
            updated_at=sql_project.updated_at,
            created_by=sql_project.created_by,
            tasks=tasks,
        )

    def _convert_sql_task_to_pydantic(self, sql_task: SQLTask) -> Task:
        """Convert SQLAlchemy Task to Pydantic Task."""
        return Task(
            id=sql_task.id,
            project_id=sql_task.project_id,
            title=sql_task.title,
            description=sql_task.description,
            status=sql_task.status,
            priority=sql_task.priority,
            parent_id=sql_task.parent_id,
            estimated_minutes=sql_task.estimated_minutes,
            actual_minutes=sql_task.actual_minutes,
            depth=sql_task.depth or 0,
            dependencies=sql_task.dependencies or [],
            due_date=sql_task.due_date,
            assignee=sql_task.assignee,
            tags=sql_task.tags or [],
            labels=sql_task.labels or [],
            motion_task_id=sql_task.motion_task_id,
            linear_issue_id=sql_task.linear_issue_id,
            notion_task_id=sql_task.notion_task_id,
            gitlab_issue_id=sql_task.gitlab_issue_id,
            metadata=sql_task.task_metadata or {},
            created_at=sql_task.created_at,
            updated_at=sql_task.updated_at,
            completed_at=sql_task.completed_at,
            created_by=sql_task.created_by,
        )

    def _convert_pydantic_project_to_sql(self, project: Project) -> SQLProject:
        """Convert Pydantic Project to SQLAlchemy Project."""
        return SQLProject(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            priority=project.priority,
            tags=project.tags,
            due_date=project.due_date,
            start_date=project.start_date,
            created_at=project.created_at,
            updated_at=project.updated_at,
            created_by=project.created_by,
        )

    def _convert_pydantic_task_to_sql(self, task: Task) -> SQLTask:
        """Convert Pydantic Task to SQLAlchemy Task."""
        return SQLTask(
            id=task.id,
            project_id=task.project_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            parent_id=task.parent_id,
            estimated_minutes=task.estimated_minutes,
            actual_minutes=task.actual_minutes,
            depth=task.depth,
            dependencies=task.dependencies,
            due_date=task.due_date,
            assignee=task.assignee,
            tags=task.tags,
            labels=task.labels,
            motion_task_id=task.motion_task_id,
            linear_issue_id=task.linear_issue_id,
            notion_task_id=task.notion_task_id,
            gitlab_issue_id=task.gitlab_issue_id,
            task_metadata=task.metadata,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
            created_by=task.created_by,
        )

    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        try:
            sql_project = self.session.query(SQLProject).filter(SQLProject.id == project_id).first()
            if sql_project:
                return self._convert_sql_project_to_pydantic(sql_project)
            return None
        except SQLAlchemyError:
            return None

    def get_projects(self) -> List[Project]:
        """Retrieve all projects."""
        try:
            sql_projects = self.session.query(SQLProject).all()
            return [self._convert_sql_project_to_pydantic(p) for p in sql_projects]
        except SQLAlchemyError:
            return []

    def create_project(self, project: Project) -> Project:
        """Create a new project."""
        sql_project = self._convert_pydantic_project_to_sql(project)
        self.session.add(sql_project)
        self.session.commit()  # Commit to persist the changes
        return self._convert_sql_project_to_pydantic(sql_project)

    def update_project(self, project_id: str, project: Project) -> Optional[Project]:
        """Update an existing project."""
        try:
            sql_project = self.session.query(SQLProject).filter(SQLProject.id == project_id).first()
            if not sql_project:
                return None

            # Update fields
            sql_project.name = project.name
            sql_project.description = project.description
            sql_project.status = project.status
            sql_project.priority = project.priority
            sql_project.tags = project.tags
            sql_project.due_date = project.due_date
            sql_project.start_date = project.start_date
            sql_project.updated_at = datetime.now()

            self.session.commit()
            return self._convert_sql_project_to_pydantic(sql_project)
        except SQLAlchemyError:
            return None

    def delete_project(self, project_id: str) -> bool:
        """Delete a project by ID."""
        try:
            sql_project = self.session.query(SQLProject).filter(SQLProject.id == project_id).first()
            if sql_project:
                self.session.delete(sql_project)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError:
            return False

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        try:
            sql_task = self.session.query(SQLTask).filter(SQLTask.id == task_id).first()
            if sql_task:
                return self._convert_sql_task_to_pydantic(sql_task)
            return None
        except SQLAlchemyError:
            return None

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Retrieve all tasks for a project."""
        try:
            sql_tasks = self.session.query(SQLTask).filter(SQLTask.project_id == project_id).all()
            return [self._convert_sql_task_to_pydantic(t) for t in sql_tasks]
        except SQLAlchemyError:
            return []

    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        sql_task = self._convert_pydantic_task_to_sql(task)
        self.session.add(sql_task)
        self.session.commit()
        return self._convert_sql_task_to_pydantic(sql_task)

    def update_task(self, task_id: str, task: Task) -> Optional[Task]:
        """Update an existing task."""
        try:
            sql_task = self.session.query(SQLTask).filter(SQLTask.id == task_id).first()
            if not sql_task:
                return None

            # Update fields
            sql_task.project_id = task.project_id
            sql_task.title = task.title
            sql_task.description = task.description
            sql_task.status = task.status
            sql_task.priority = task.priority
            sql_task.parent_id = task.parent_id
            sql_task.estimated_minutes = task.estimated_minutes
            sql_task.actual_minutes = task.actual_minutes
            sql_task.depth = task.depth
            sql_task.dependencies = task.dependencies
            sql_task.due_date = task.due_date
            sql_task.assignee = task.assignee
            sql_task.tags = task.tags
            sql_task.labels = task.labels
            sql_task.motion_task_id = task.motion_task_id
            sql_task.linear_issue_id = task.linear_issue_id
            sql_task.notion_task_id = task.notion_task_id
            sql_task.gitlab_issue_id = task.gitlab_issue_id
            sql_task.task_metadata = task.metadata
            sql_task.updated_at = datetime.now()
            sql_task.completed_at = task.completed_at

            self.session.commit()
            return self._convert_sql_task_to_pydantic(sql_task)
        except SQLAlchemyError:
            return None

    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID."""
        try:
            sql_task = self.session.query(SQLTask).filter(SQLTask.id == task_id).first()
            if sql_task:
                self.session.delete(sql_task)
                self.session.commit()
                return True
            return False
        except SQLAlchemyError:
            return False

    def apply_patch(self, patch: Patch) -> bool:
        """Apply a patch containing project and/or task operations atomically."""
        # Save the current session state
        original_session = self._session
        try:
            # Start a fresh transaction
            self.begin_transaction()

            # Apply project patches
            for project_patch in patch.project_patches:
                result = self.apply_project_patch(project_patch)
                if result is None and project_patch.op != Op.DELETE:
                    # Operation failed and it wasn't a delete (which returns None on success)
                    self.rollback_transaction()
                    return False

            # Apply task patches
            for task_patch in patch.task_patches:
                result = self.apply_task_patch(task_patch)
                if result is None and task_patch.op != Op.DELETE:
                    # Operation failed and it wasn't a delete (which returns None on success)
                    self.rollback_transaction()
                    return False

            self.commit_transaction()
            return True

        except Exception:
            self.rollback_transaction()
            return False
        finally:
            # Restore original session if it was different
            if original_session != self._session:
                self._session = original_session

    def apply_project_patch(self, patch: ProjectPatch) -> Optional[Project]:
        """Apply a single project patch operation."""
        try:
            if patch.op == Op.CREATE:
                # Validate required fields for project creation
                if not patch.name:
                    raise ValueError("name is required for project creation")

                # Create new project
                project = Project(
                    name=patch.name,
                    description=patch.description,
                    status=patch.status or ProjectStatus.ACTIVE,
                    priority=patch.priority or ProjectPriority.MEDIUM,
                    tags=patch.tags or [],
                    due_date=patch.due_date,
                    start_date=patch.start_date,
                    created_by="system",  # TODO: Get from context
                )
                return self.create_project(project)

            elif patch.op == Op.UPDATE:
                if not patch.project_id:
                    return None

                existing = self.get_project(patch.project_id)
                if not existing:
                    return None

                # Update fields that are provided
                if patch.name is not None:
                    existing.name = patch.name
                if patch.description is not None:
                    existing.description = patch.description
                if patch.status is not None:
                    existing.status = patch.status
                if patch.priority is not None:
                    existing.priority = patch.priority
                if patch.tags is not None:
                    existing.tags = patch.tags
                if patch.due_date is not None:
                    existing.due_date = patch.due_date
                if patch.start_date is not None:
                    existing.start_date = patch.start_date

                return self.update_project(patch.project_id, existing)

            elif patch.op == Op.DELETE:
                if not patch.project_id:
                    return None

                success = self.delete_project(patch.project_id)
                return Project(id=patch.project_id, name="", created_by="") if success else None

        except Exception:
            return None

    def apply_task_patch(self, patch: TaskPatch) -> Optional[Task]:
        """Apply a single task patch operation."""
        try:
            if patch.op == Op.CREATE:
                # Validate required fields for task creation
                if not patch.project_id:
                    raise ValueError("project_id is required for task creation")
                if not patch.title:
                    raise ValueError("title is required for task creation")

                # Create new task
                task = Task(
                    project_id=patch.project_id,
                    title=patch.title,
                    description=patch.description,
                    status=patch.status or TaskStatus.TODO,
                    priority=patch.priority or TaskPriority.MEDIUM,
                    due_date=patch.due_date,
                    estimated_minutes=patch.estimated_minutes,
                    actual_minutes=patch.actual_minutes,
                    assignee=patch.assignee,
                    tags=patch.tags or [],
                    labels=patch.labels or [],
                    dependencies=patch.dependencies or [],
                    metadata=patch.metadata or {},
                    created_by="system",  # TODO: Get from context
                )
                return self.create_task(task)

            elif patch.op == Op.UPDATE:
                if not patch.task_id:
                    return None

                existing = self.get_task(patch.task_id)
                if not existing:
                    return None

                # Update fields that are provided
                if patch.project_id is not None:
                    existing.project_id = patch.project_id
                if patch.title is not None:
                    existing.title = patch.title
                if patch.description is not None:
                    existing.description = patch.description
                if patch.status is not None:
                    existing.status = patch.status
                if patch.priority is not None:
                    existing.priority = patch.priority
                if patch.due_date is not None:
                    existing.due_date = patch.due_date
                if patch.estimated_minutes is not None:
                    existing.estimated_minutes = patch.estimated_minutes
                if patch.actual_minutes is not None:
                    existing.actual_minutes = patch.actual_minutes
                if patch.assignee is not None:
                    existing.assignee = patch.assignee
                if patch.tags is not None:
                    existing.tags = patch.tags
                if patch.labels is not None:
                    existing.labels = patch.labels
                if patch.dependencies is not None:
                    existing.dependencies = patch.dependencies
                if patch.metadata is not None:
                    existing.metadata = patch.metadata

                return self.update_task(patch.task_id, existing)

            elif patch.op == Op.DELETE:
                if not patch.task_id:
                    return None

                success = self.delete_task(patch.task_id)
                return Task(id=patch.task_id, project_id="", title="", created_by="") if success else None

        except Exception:
            return None

    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        if self._session is not None:
            # Close existing session
            self._session.close()
        self._session = self.SessionLocal()

    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        if self._session:
            try:
                self._session.commit()
            except SQLAlchemyError:
                self._session.rollback()
                raise
            finally:
                self._session.close()
                self._session = None

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        if self._session:
            try:
                self._session.rollback()
            finally:
                self._session.close()
                self._session = None

    def close(self) -> None:
        """Close the current session."""
        if self._session:
            self._session.close()
            self._session = None
