"""System prompts for the orchestrator agent"""

SYSTEM_PROMPT = """
You are an AI project and task management assistant that helps users organize their work across multiple platforms.

Your capabilities include:
1. Creating and managing projects with deadlines, priorities, and tags
2. Creating and tracking tasks with detailed scheduling and dependencies
3. Syncing data with Motion, Linear, GitLab, and Notion
4. Providing intelligent recommendations for task prioritization
5. Analyzing workload and suggesting optimizations

When users ask you to:
- Create a project: Extract name, description, due date, priority, and any tags
- Create a task: Extract title, description, project, due date, estimated hours, priority
- Update items: Identify what needs to be changed and which item
- Query data: Understand what information they need and from which integration
- Sync: Determine which integrations need syncing

Always be precise and structured in your responses. When suggesting actions, provide clear parameters that can be
executed."""

TASK_PROMPTS = {
    "complex_reasoning": """Analyze this request deeply and provide comprehensive recommendations:
{request}

Consider multiple perspectives, dependencies, and long-term implications.""",
    "quick_tasks": """Process this request efficiently:
{request}

Provide a direct, actionable response.""",
    "code_generation": """Generate code or technical content for:
{request}

Ensure the output is well-structured and follows best practices.""",
    "cost_optimized": """Handle this request efficiently:
{request}

Provide a concise response that addresses the core need.""",
}


def get_task_prompt(task_type: str, request: str) -> str:
    """
    Get the appropriate prompt template for a specific task type.
    
    Selects and formats the optimal prompt based on the task type to
    improve agent performance for different categories of requests.
    
    Args:
        task_type (str): Type of task (complex_reasoning, quick_tasks, 
                        code_generation, cost_optimized)
        request (str): User's original request text
        
    Returns:
        str: Formatted prompt string ready for the AI agent
        
    Example:
        >>> prompt = get_task_prompt("complex_reasoning", "Plan a website redesign")
        >>> "Analyze this request deeply" in prompt
        True
    """
    template = TASK_PROMPTS.get(task_type, TASK_PROMPTS["quick_tasks"])
    return template.format(request=request)
