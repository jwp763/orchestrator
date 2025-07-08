"""Integration tests for PlannerAgent with realistic project scenarios."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent.planner_agent import PlannerAgent
from src.models.patch import Op, Patch
from src.models.project import ProjectPriority, ProjectStatus
from src.models.task import TaskPriority, TaskStatus


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.default_provider = "anthropic"
    settings.get_api_key.return_value = "test-key"

    # Mock provider config
    mock_provider_config = MagicMock()
    mock_provider_config.default = "claude-3-haiku-20240307"

    mock_providers = MagicMock()
    mock_providers.providers = {"anthropic": mock_provider_config}

    settings.providers = mock_providers
    return settings


class TestPlannerAgentRealisticScenarios:
    """Integration tests with realistic project ideas and expected outputs."""

    @pytest.mark.asyncio
    async def test_mobile_app_project(self, mock_settings):
        """Test planning a mobile app development project."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=5)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Fitness Tracking Mobile App",
                    "description": "Cross-platform mobile app for tracking workouts, nutrition, and progress with social features",
                    "status": "planning",
                    "priority": "high",
                    "tags": ["mobile", "fitness", "react-native", "app"],
                    "estimated_total_minutes": 9600,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Market Research & Requirements",
                    "description": "Analyze competitors and define detailed requirements",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 1200,
                },
                {
                    "op": "create",
                    "title": "UI/UX Design Phase",
                    "description": "Create user flows, wireframes, and high-fidelity designs",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 2400,
                },
                {
                    "op": "create",
                    "title": "Core App Development",
                    "description": "Develop main features: tracking, data storage, user authentication",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 4800,
                },
                {
                    "op": "create",
                    "title": "Social Features Implementation",
                    "description": "Add sharing, social feeds, and community features",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 2400,
                },
                {
                    "op": "create",
                    "title": "Testing & App Store Deployment",
                    "description": "QA testing, beta testing, and publish to app stores",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 800,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = """I want to build a fitness tracking mobile app that helps people track their workouts,
            nutrition, and progress. It should have social features so users can share achievements and motivate
            each other. I want it to work on both iOS and Android."""

            result = await agent.get_diff(user_input)

            # Validate project structure
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 5

            project = result.project_patches[0]
            assert "Fitness" in project.name
            assert "mobile" in project.tags
            assert project.priority == ProjectPriority.HIGH

            # Validate milestone distribution
            total_minutes = sum(task.estimated_minutes for task in result.task_patches)
            expected_minutes = 1200 + 2400 + 4800 + 2400 + 800  # Sum from expected_response
            assert total_minutes == expected_minutes

            # Ensure critical phases are marked appropriately
            research_task = next(task for task in result.task_patches if "Research" in task.title)
            assert research_task.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_ecommerce_platform_project(self, mock_settings):
        """Test planning an e-commerce platform project."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=6)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Artisan Marketplace E-commerce Platform",
                    "description": "Full-featured e-commerce platform for artisans to sell handmade products with payment processing and inventory management",
                    "status": "planning",
                    "priority": "critical",
                    "tags": ["ecommerce", "marketplace", "fullstack", "payment"],
                    "estimated_total_minutes": 19200,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Platform Architecture Design",
                    "description": "Design system architecture, database schema, and technology stack",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 2400,
                },
                {
                    "op": "create",
                    "title": "User Authentication & Profiles",
                    "description": "Implement user registration, login, and profile management",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 2400,
                },
                {
                    "op": "create",
                    "title": "Product Catalog System",
                    "description": "Build product listing, search, filtering, and category management",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 4800,
                },
                {
                    "op": "create",
                    "title": "Shopping Cart & Checkout",
                    "description": "Implement cart functionality and secure checkout process",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 3600,
                },
                {
                    "op": "create",
                    "title": "Payment Integration",
                    "description": "Integrate payment processors and handle transactions securely",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 3600,
                },
                {
                    "op": "create",
                    "title": "Admin Dashboard & Analytics",
                    "description": "Build seller dashboard for inventory and sales management",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 2400,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = """Create an e-commerce marketplace where artisans can sell their handmade products.
            It needs user accounts, product listings, shopping cart, secure payments, and a dashboard for
            sellers to manage their inventory and view sales analytics."""

            result = await agent.get_diff(user_input)

            # Validate complex project structure
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 6

            project = result.project_patches[0]
            assert "Marketplace" in project.name or "E-commerce" in project.name
            assert project.priority == ProjectPriority.CRITICAL
            assert "payment" in project.tags

            # Validate security-critical tasks are prioritized
            payment_task = next(task for task in result.task_patches if "Payment" in task.title)
            assert payment_task.priority == TaskPriority.CRITICAL

            auth_task = next(task for task in result.task_patches if "Authentication" in task.title)
            assert auth_task.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]

    @pytest.mark.asyncio
    async def test_data_analysis_project(self, mock_settings):
        """Test planning a data analysis and visualization project."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=4)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Customer Behavior Analytics Dashboard",
                    "description": "Analyze customer data to identify patterns and create interactive dashboards for business insights",
                    "status": "planning",
                    "priority": "medium",
                    "tags": ["data-science", "analytics", "dashboard", "python"],
                    "estimated_total_minutes": 4800,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Data Collection & Cleaning",
                    "description": "Gather customer data from various sources and clean for analysis",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 1200,
                },
                {
                    "op": "create",
                    "title": "Exploratory Data Analysis",
                    "description": "Perform statistical analysis to identify patterns and insights",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 1800,
                },
                {
                    "op": "create",
                    "title": "Dashboard Development",
                    "description": "Build interactive visualizations and dashboard interface",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 1800,
                },
                {
                    "op": "create",
                    "title": "Reporting & Deployment",
                    "description": "Create automated reports and deploy dashboard for stakeholders",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 600,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = """I need to analyze our customer data to understand buying patterns and create
            visualizations. The goal is to build a dashboard that shows key metrics and insights to help
            with business decisions."""

            result = await agent.get_diff(user_input)

            # Validate data science project structure
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 4

            project = result.project_patches[0]
            assert "Analytics" in project.name or "Data" in project.name
            assert "data-science" in project.tags or "analytics" in project.tags

            # Verify logical task progression
            task_titles = [task.title for task in result.task_patches]
            assert any("Data Collection" in title or "Cleaning" in title for title in task_titles)
            assert any("Analysis" in title for title in task_titles)
            assert any("Dashboard" in title or "Visualization" in title for title in task_titles)

    @pytest.mark.asyncio
    async def test_minimal_project_without_milestones(self, mock_settings):
        """Test planning a simple project without milestone breakdown."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=False)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Personal Blog Website",
                    "description": "Simple personal blog to share thoughts and experiences",
                    "status": "planning",
                    "priority": "low",
                    "tags": ["blog", "personal", "simple"],
                }
            ],
            "task_patches": [],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = "I want to create a simple personal blog where I can write about my thoughts and experiences"

            result = await agent.get_diff(user_input)

            # Validate simple project structure
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 0

            project = result.project_patches[0]
            assert "Blog" in project.name
            assert project.priority == ProjectPriority.LOW
            assert "simple" in project.tags or "personal" in project.tags

    @pytest.mark.asyncio
    async def test_research_project_with_context(self, mock_settings):
        """Test planning with additional context information."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=3)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Machine Learning Model for Fraud Detection",
                    "description": "Research and develop ML model for detecting fraudulent transactions in real-time",
                    "status": "planning",
                    "priority": "critical",
                    "tags": ["machine-learning", "fraud-detection", "research", "security"],
                    "estimated_total_minutes": 7200,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Literature Review & Data Collection",
                    "description": "Research existing approaches and gather training datasets",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 2400,
                },
                {
                    "op": "create",
                    "title": "Model Development & Training",
                    "description": "Develop and train ML models using various algorithms",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 4800,
                },
                {
                    "op": "create",
                    "title": "Evaluation & Production Deployment",
                    "description": "Evaluate model performance and deploy to production",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 2400,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = "Develop a machine learning model to detect fraudulent credit card transactions"
            context = {
                "domain": "fintech",
                "timeline": "3 months",
                "team_size": "2 data scientists",
                "create_milestones": True,
            }

            result = await agent.get_diff(user_input, context=context)

            # Validate research project structure
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 3

            project = result.project_patches[0]
            assert "Machine Learning" in project.name or "ML" in project.name
            assert "Fraud" in project.name
            assert project.priority == ProjectPriority.CRITICAL
            assert "security" in project.tags

            # Verify research-oriented tasks
            literature_task = next(
                task for task in result.task_patches if "Literature" in task.title or "Research" in task.title
            )
            assert literature_task.priority in [TaskPriority.HIGH, TaskPriority.CRITICAL]

    @pytest.mark.asyncio
    async def test_enterprise_software_project(self, mock_settings):
        """Test planning a large enterprise software project."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=5)

        expected_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Enterprise Resource Planning (ERP) System",
                    "description": "Comprehensive ERP system for managing HR, finance, inventory, and operations across the organization",
                    "status": "planning",
                    "priority": "critical",
                    "tags": ["enterprise", "erp", "fullstack", "database", "integration"],
                    "estimated_total_minutes": 120000,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Requirements Gathering & System Analysis",
                    "description": "Detailed requirements analysis and system architecture design",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 24000,
                },
                {
                    "op": "create",
                    "title": "Core Platform Development",
                    "description": "Build foundational platform with user management and core services",
                    "status": "todo",
                    "priority": "critical",
                    "estimated_minutes": 48000,
                },
                {
                    "op": "create",
                    "title": "HR Module Implementation",
                    "description": "Develop human resources management functionality",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 24000,
                },
                {
                    "op": "create",
                    "title": "Finance & Inventory Modules",
                    "description": "Implement financial management and inventory tracking systems",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 36000,
                },
                {
                    "op": "create",
                    "title": "Integration & Deployment",
                    "description": "System integration, testing, and enterprise deployment",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 24000,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(expected_response)

            user_input = """Build a comprehensive ERP system for our company that integrates HR management,
            financial accounting, inventory tracking, and operations management. It needs to handle multiple
            departments and provide real-time reporting."""

            result = await agent.get_diff(user_input)

            # Validate enterprise-scale project
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 5

            project = result.project_patches[0]
            assert "ERP" in project.name or "Enterprise" in project.name
            assert project.priority == ProjectPriority.CRITICAL
            assert "enterprise" in project.tags

            # Validate large time estimates
            total_hours = sum(task.estimated_minutes for task in result.task_patches) / 60
            assert total_hours >= 1000  # Should be a large project

            # Ensure critical foundation tasks are prioritized
            requirements_task = next(task for task in result.task_patches if "Requirements" in task.title)
            assert requirements_task.priority == TaskPriority.CRITICAL

            platform_task = next(
                task for task in result.task_patches if "Platform" in task.title or "Core" in task.title
            )
            assert platform_task.priority == TaskPriority.CRITICAL

    @pytest.mark.asyncio
    async def test_project_idea_edge_cases(self, mock_settings):
        """Test handling of various edge cases in project ideas."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True)

        edge_case_scenarios = [
            # Vague input
            "Make something cool",
            # Very technical input
            "Implement a distributed microservices architecture with Kubernetes orchestration",
            # Non-technical input
            "Help me organize my life better",
            # Multiple projects in one request
            "Build a website and also create a mobile app",
        ]

        for user_input in edge_case_scenarios:
            expected_response = {
                "project_patches": [
                    {
                        "op": "create",
                        "name": f"Project for: {user_input[:30]}...",
                        "description": f"Generated project based on: {user_input}",
                        "status": "planning",
                        "priority": "medium",
                        "tags": ["generated"],
                    }
                ],
                "task_patches": [],
            }

            with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
                mock_llm.return_value = Patch.model_validate(expected_response)

                result = await agent.get_diff(user_input)

                # Should handle edge cases gracefully
                assert isinstance(result, Patch)
                assert len(result.project_patches) >= 1

                project = result.project_patches[0]
                assert project.name is not None
                assert len(project.name) >= 3
                assert project.description is not None
