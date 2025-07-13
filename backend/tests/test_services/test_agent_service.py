"""
Unit and integration tests for AgentService.

Tests the orchestration service layer for AI agent coordination,
including unit tests with mocked dependencies and integration tests
with real storage and agent connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..test_api.test_database_isolation import TestDatabaseIsolation
from src.orchestration.agent_service import AgentService
from src.orchestration.project_service import ProjectService
from src.orchestration.task_service import TaskService
from src.storage.interface import StorageInterface
from src.storage.sql_implementation import SQLStorage
from src.agent.planner_agent import PlannerAgent
from src.models.project import (
    Project, ProjectCreate, ProjectStatus, ProjectPriority
)
from src.models.task import (
    Task, TaskCreate, TaskStatus, TaskPriority
)
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op


class TestAgentServiceUnit:
    """Unit tests for AgentService with mocked dependencies."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage interface for unit tests."""
        return Mock(spec=StorageInterface)

    @pytest.fixture
    def mock_project_service(self):
        """Mock project service for unit tests."""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def mock_task_service(self):
        """Mock task service for unit tests."""
        return Mock(spec=TaskService)

    @pytest.fixture
    def mock_planner_agent(self):
        """Mock planner agent for unit tests."""
        return Mock(spec=PlannerAgent)

    @pytest.fixture
    def agent_service(self, mock_storage, mock_project_service, mock_task_service):
        """AgentService instance with mocked dependencies."""
        service = AgentService(
            storage=mock_storage,
            project_service=mock_project_service,
            task_service=mock_task_service
        )
        return service

    @pytest.fixture
    def sample_project(self):
        """Sample project for testing."""
        return Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "ai"],
            created_by="ai_agent",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def sample_tasks(self):
        """Sample tasks for testing."""
        return [
            Task(
                id="task-1",
                title="Task 1",
                description="First task",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                project_id="test-project-1",
                created_by="ai_agent"
            ),
            Task(
                id="task-2", 
                title="Task 2",
                description="Second task",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                project_id="test-project-1",
                created_by="ai_agent"
            )
        ]

    def test_init_default_dependencies(self):
        """Test AgentService initialization with default dependencies."""
        service = AgentService()
        assert isinstance(service.storage, SQLStorage)
        assert isinstance(service.project_service, ProjectService)
        assert isinstance(service.task_service, TaskService)
        assert isinstance(service.planner_agent, PlannerAgent)

    def test_init_custom_dependencies(self, mock_storage, mock_project_service, mock_task_service):
        """Test AgentService initialization with custom dependencies."""
        service = AgentService(
            storage=mock_storage,
            project_service=mock_project_service,
            task_service=mock_task_service
        )
        assert service.storage is mock_storage
        assert service.project_service is mock_project_service
        assert service.task_service is mock_task_service

    @patch('src.orchestration.agent_service.PlannerAgent')
    def test_generate_project_from_idea_success(self, mock_planner_class, agent_service, 
                                               mock_project_service, mock_task_service, 
                                               sample_project, sample_tasks):
        """Test successful project generation from idea."""
        # Setup mocks
        mock_planner = Mock()
        mock_planner_class.return_value = mock_planner
        agent_service.planner_agent = mock_planner
        
        # Mock planner response
        mock_planner.plan_project.return_value = {
            "project": {
                "name": "Test Project",
                "description": "A test project",
                "priority": "high",
                "tags": ["test", "ai"]
            },
            "tasks": [
                {
                    "title": "Task 1",
                    "description": "First task",
                    "priority": "high"
                },
                {
                    "title": "Task 2", 
                    "description": "Second task",
                    "priority": "medium"
                }
            ]
        }
        
        # Mock service responses
        mock_project_service.create_project.return_value = sample_project
        mock_task_service.create_task.side_effect = sample_tasks
        
        # Execute
        result = agent_service.generate_project_from_idea(
            idea="Create a test project with some tasks",
            context={"domain": "testing"},
            created_by="test_user"
        )
        
        # Verify
        assert result["project"] == sample_project
        assert len(result["tasks"]) == 2
        assert result["tasks"] == sample_tasks
        
        mock_planner.plan_project.assert_called_once()
        mock_project_service.create_project.assert_called_once()
        assert mock_task_service.create_task.call_count == 2

    @patch('src.orchestration.agent_service.PlannerAgent')
    def test_generate_project_from_idea_planner_error(self, mock_planner_class, agent_service):
        """Test project generation when planner fails."""
        mock_planner = Mock()
        mock_planner_class.return_value = mock_planner
        agent_service.planner_agent = mock_planner
        
        mock_planner.plan_project.side_effect = Exception("Planner failed")
        
        with pytest.raises(Exception, match="Planner failed"):
            agent_service.generate_project_from_idea(
                idea="Create a project",
                created_by="test_user"
            )

    def test_decompose_task_success(self, agent_service, mock_task_service, sample_tasks):
        """Test successful task decomposition."""
        parent_task = Task(
            id="parent-task",
            title="Complex Task",
            description="A complex task to decompose",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id="test-project-1",
            created_by="test_user"
        )
        
        with patch.object(agent_service, 'planner_agent') as mock_planner:
            mock_planner.decompose_task.return_value = {
                "subtasks": [
                    {
                        "title": "Subtask 1",
                        "description": "First subtask",
                        "priority": "medium"
                    },
                    {
                        "title": "Subtask 2",
                        "description": "Second subtask", 
                        "priority": "low"
                    }
                ]
            }
            
            mock_task_service.get_task.return_value = parent_task
            mock_task_service.create_task.side_effect = sample_tasks[:2]
            
            result = agent_service.decompose_task(
                task_id="parent-task",
                context={"level": "detailed"},
                created_by="test_user"
            )
            
            assert result["parent_task"] == parent_task
            assert len(result["subtasks"]) == 2
            assert result["subtasks"] == sample_tasks[:2]
            
            mock_planner.decompose_task.assert_called_once()
            mock_task_service.get_task.assert_called_once_with("parent-task")
            assert mock_task_service.create_task.call_count == 2

    def test_decompose_task_not_found(self, agent_service, mock_task_service):
        """Test task decomposition when parent task doesn't exist."""
        mock_task_service.get_task.return_value = None
        
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            agent_service.decompose_task("nonexistent", created_by="test_user")

    def test_generate_patch_from_request_success(self, agent_service, mock_project_service, sample_project):
        """Test successful patch generation from natural language request."""
        mock_project_service.get_project.return_value = sample_project
        
        with patch.object(agent_service, 'planner_agent') as mock_planner:
            mock_planner.generate_patch.return_value = {
                "operations": [
                    {
                        "op": "replace",
                        "path": "/name",
                        "value": "Updated Project Name"
                    }
                ]
            }
            
            result = agent_service.generate_patch_from_request(
                entity_type="project",
                entity_id="test-project-1",
                request="Change the project name to 'Updated Project Name'",
                created_by="test_user"
            )
            
            assert isinstance(result, ProjectPatch)
            assert result.project_id == "test-project-1"
            assert len(result.operations) == 1
            assert result.operations[0].op == "replace"
            assert result.operations[0].path == "/name"
            assert result.operations[0].value == "Updated Project Name"
            
            mock_planner.generate_patch.assert_called_once()

    def test_generate_patch_from_request_invalid_entity(self, agent_service, mock_project_service):
        """Test patch generation with invalid entity."""
        mock_project_service.get_project.return_value = None
        
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            agent_service.generate_patch_from_request(
                entity_type="project",
                entity_id="nonexistent",
                request="Update something",
                created_by="test_user"
            )

    def test_generate_patch_from_request_invalid_entity_type(self, agent_service):
        """Test patch generation with invalid entity type."""
        with pytest.raises(ValueError, match="Unsupported entity type: invalid"):
            agent_service.generate_patch_from_request(
                entity_type="invalid",
                entity_id="test-id",
                request="Update something",
                created_by="test_user"
            )

    def test_apply_ai_suggested_patch_success(self, agent_service, mock_project_service, sample_project):
        """Test successful application of AI-suggested patch."""
        patch = ProjectPatch(
            project_id="test-project-1",
            operations=[Op(op="replace", path="/name", value="AI Updated Name")],
            created_by="ai_agent"
        )
        updated_project = sample_project.model_copy(update={"name": "AI Updated Name"})
        
        mock_project_service.apply_patch.return_value = updated_project
        
        result = agent_service.apply_ai_suggested_patch(patch)
        
        assert result == updated_project
        mock_project_service.apply_patch.assert_called_once_with(patch)

    def test_conversation_workflow_success(self, agent_service, mock_project_service, 
                                         mock_task_service, sample_project, sample_tasks):
        """Test successful conversation workflow orchestration."""
        conversation_context = {
            "intent": "create_project_with_tasks",
            "idea": "Build a todo app",
            "user_preferences": {"framework": "react"}
        }
        
        with patch.object(agent_service, 'generate_project_from_idea') as mock_generate:
            mock_generate.return_value = {
                "project": sample_project,
                "tasks": sample_tasks
            }
            
            result = agent_service.conversation_workflow(
                conversation_context=conversation_context,
                created_by="conversation_user"
            )
            
            assert result["project"] == sample_project
            assert result["tasks"] == sample_tasks
            assert "conversation_id" in result
            
            mock_generate.assert_called_once()


class TestAgentServiceIntegration(TestDatabaseIsolation):
    """Integration tests for AgentService with real storage."""

    @pytest.fixture
    def agent_service(self, isolated_storage):
        """AgentService with isolated database."""
        project_service = ProjectService(storage=isolated_storage)
        task_service = TaskService(storage=isolated_storage)
        return AgentService(
            storage=isolated_storage,
            project_service=project_service,
            task_service=task_service
        )

    @patch('src.agent.planner_agent.PlannerAgent.plan_project')
    def test_project_generation_integration(self, mock_plan_project, agent_service):
        """Test project generation with real storage integration."""
        # Mock the AI agent response
        mock_plan_project.return_value = {
            "project": {
                "name": "Integration Test Project",
                "description": "Generated by AI for integration testing",
                "priority": "high",
                "tags": ["ai-generated", "integration"]
            },
            "tasks": [
                {
                    "title": "Setup Project Structure",
                    "description": "Create initial project structure",
                    "priority": "high",
                    "estimated_minutes": 60
                },
                {
                    "title": "Implement Core Features",
                    "description": "Build the main functionality",
                    "priority": "medium",
                    "estimated_minutes": 240
                }
            ]
        }
        
        # Execute the workflow
        result = agent_service.generate_project_from_idea(
            idea="Create a task management application",
            context={"domain": "productivity", "complexity": "medium"},
            created_by="ai_integration_test"
        )
        
        # Verify project creation
        assert result["project"] is not None
        assert result["project"].name == "Integration Test Project"
        assert result["project"].created_by == "ai_integration_test"
        
        # Verify task creation
        assert len(result["tasks"]) == 2
        assert result["tasks"][0].title == "Setup Project Structure"
        assert result["tasks"][1].title == "Implement Core Features"
        
        # Verify data persistence
        project_id = result["project"].id
        retrieved_project = agent_service.project_service.get_project(project_id)
        assert retrieved_project is not None
        assert retrieved_project.name == "Integration Test Project"
        
        # Verify tasks are linked to project
        project_tasks = agent_service.task_service.list_tasks(project_id=project_id)
        assert len(project_tasks) == 2
        task_titles = [task.title for task in project_tasks]
        assert "Setup Project Structure" in task_titles
        assert "Implement Core Features" in task_titles

    @patch('src.agent.planner_agent.PlannerAgent.decompose_task')
    def test_task_decomposition_integration(self, mock_decompose_task, agent_service):
        """Test task decomposition with real storage integration."""
        # Create a project first
        project = agent_service.project_service.create_project(ProjectCreate(
            name="Decomposition Test Project",
            description="Project for testing task decomposition",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="decomp_test_user"
        ))
        
        # Create a parent task
        parent_task = agent_service.task_service.create_task(TaskCreate(
            title="Complex Integration Task",
            description="A complex task that needs decomposition",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            estimated_minutes=480,
            created_by="decomp_test_user"
        ))
        
        # Mock the AI decomposition response
        mock_decompose_task.return_value = {
            "subtasks": [
                {
                    "title": "Research Requirements",
                    "description": "Analyze and document requirements",
                    "priority": "high",
                    "estimated_minutes": 120
                },
                {
                    "title": "Design Solution",
                    "description": "Create technical design",
                    "priority": "high", 
                    "estimated_minutes": 180
                },
                {
                    "title": "Implement Solution",
                    "description": "Code the solution",
                    "priority": "medium",
                    "estimated_minutes": 180
                }
            ]
        }
        
        # Execute decomposition
        result = agent_service.decompose_task(
            task_id=parent_task.id,
            context={"detail_level": "high", "methodology": "agile"},
            created_by="decomp_test_user"
        )
        
        # Verify decomposition results
        assert result["parent_task"].id == parent_task.id
        assert len(result["subtasks"]) == 3
        
        # Verify subtasks are properly linked
        for subtask in result["subtasks"]:
            assert subtask.parent_id == parent_task.id
            assert subtask.project_id == project.id
            assert subtask.created_by == "decomp_test_user"
        
        # Verify hierarchy retrieval
        hierarchy = agent_service.task_service.get_task_hierarchy(parent_task.id)
        assert len(hierarchy["children"]) == 3
        child_titles = [child.title for child in hierarchy["children"]]
        assert "Research Requirements" in child_titles
        assert "Design Solution" in child_titles
        assert "Implement Solution" in child_titles

    @patch('src.agent.planner_agent.PlannerAgent.generate_patch')
    def test_patch_generation_integration(self, mock_generate_patch, agent_service):
        """Test AI patch generation with real storage integration."""
        # Create a project
        project = agent_service.project_service.create_project(ProjectCreate(
            name="Patch Test Project",
            description="Project for testing patch generation",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
            created_by="patch_test_user"
        ))
        
        # Mock AI patch generation
        mock_generate_patch.return_value = {
            "operations": [
                {
                    "op": "replace",
                    "path": "/name",
                    "value": "AI Enhanced Project Name"
                },
                {
                    "op": "replace",
                    "path": "/status", 
                    "value": "active"
                },
                {
                    "op": "add",
                    "path": "/tags/-",
                    "value": "ai-enhanced"
                }
            ]
        }
        
        # Generate patch
        patch = agent_service.generate_patch_from_request(
            entity_type="project",
            entity_id=project.id,
            request="Update the project name to be more descriptive and mark it as active",
            created_by="ai_assistant"
        )
        
        # Apply patch
        updated_project = agent_service.apply_ai_suggested_patch(patch)
        
        # Verify patch application
        assert updated_project.name == "AI Enhanced Project Name"
        assert updated_project.status == ProjectStatus.ACTIVE
        assert "ai-enhanced" in updated_project.tags
        
        # Verify persistence
        retrieved_project = agent_service.project_service.get_project(project.id)
        assert retrieved_project.name == "AI Enhanced Project Name"
        assert retrieved_project.status == ProjectStatus.ACTIVE

    def test_error_handling_integration(self, agent_service):
        """Test error handling with real storage integration."""
        # Test project generation with invalid entity
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            agent_service.generate_patch_from_request(
                entity_type="project",
                entity_id="nonexistent",
                request="Update something",
                created_by="test_user"
            )
        
        # Test task decomposition with invalid task
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            agent_service.decompose_task("nonexistent", created_by="test_user")

    def test_conversation_workflow_integration(self, agent_service):
        """Test complete conversation workflow integration."""
        conversation_context = {
            "intent": "create_simple_project",
            "user_input": "I need a project to track my daily tasks",
            "preferences": {
                "priority": "high",
                "tags": ["personal", "daily"]
            }
        }
        
        with patch.object(agent_service, 'generate_project_from_idea') as mock_generate:
            # Mock the project generation to return real objects
            test_project = agent_service.project_service.create_project(ProjectCreate(
                name="Daily Task Tracker",
                description="Track daily tasks and activities",
                status=ProjectStatus.ACTIVE,
                priority=ProjectPriority.HIGH,
                tags=["personal", "daily"],
                created_by="conversation_user"
            ))
            
            mock_generate.return_value = {
                "project": test_project,
                "tasks": []
            }
            
            result = agent_service.conversation_workflow(
                conversation_context=conversation_context,
                created_by="conversation_user"
            )
            
            assert result["project"] is not None
            assert result["project"].name == "Daily Task Tracker"
            assert "conversation_id" in result
            assert isinstance(result["conversation_id"], str)