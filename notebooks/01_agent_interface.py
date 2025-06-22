# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Interface
# MAGIC Interactive notebook for chatting with the orchestrator agent

# COMMAND ----------

# MAGIC %pip install pydantic pydantic-ai delta-spark pyyaml anthropic openai google-generativeai

# COMMAND ----------

import sys
sys.path.append("..")

from src.agent import get_agent
from src.storage import DeltaManager, StateManager
from src.models import AgentRequest, AgentContext
from src.config import get_settings
import json

# COMMAND ----------

# Initialize components
settings = get_settings()
delta_manager = DeltaManager(spark)
state_manager = StateManager(delta_manager)
agent = get_agent()

# COMMAND ----------

# Get or create user
user_id = None
users = delta_manager.get_projects({"name": "Default User"})
if users:
    user_id = users[0]["id"]
else:
    user = delta_manager.create_user({"name": "Default User", "email": "user@example.com"})
    user_id = user["id"]

print(f"Using user: {user_id}")

# COMMAND ----------

# Create a new conversation
conversation = state_manager.create_conversation(user_id)
print(f"Started conversation: {conversation.conversation_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Chat with the Agent
# MAGIC 
# MAGIC Example requests:
# MAGIC - "Create a project called 'Q1 Planning' with a due date of March 31"
# MAGIC - "Add a task to review documentation with 2 hours estimate"
# MAGIC - "Show me all active projects"
# MAGIC - "Update the Q1 Planning project status to active"

# COMMAND ----------

def chat(message: str, task_type: str = None, preferred_provider: str = None):
    """Send a message to the agent"""
    request = AgentRequest(
        message=message,
        task_type=task_type,
        preferred_provider=preferred_provider
    )
    
    print(f"You: {message}")
    print("-" * 50)
    
    # Process request
    response = agent.process_request_sync(request)
    
    print(f"Agent ({response.provider_used}:{response.model_used}): {response.message}")
    
    if response.actions:
        print("\nSuggested actions:")
        for i, action in enumerate(response.actions, 1):
            print(f"{i}. {action.action_type}: {json.dumps(action.parameters, indent=2)}")
    
    if response.errors:
        print(f"\nErrors: {response.errors}")
    
    # Save to conversation history
    state_manager.add_message(conversation.conversation_id, request, response)
    
    return response

# COMMAND ----------

# Example: Create a project
response = chat("Create a new project called 'Personal Task Manager Development' with a due date of end of next month. This is for building our task management system.")

# COMMAND ----------

# Example: Add tasks
response = chat("Add the following tasks to the Personal Task Manager Development project: 1) Implement Motion API client (8 hours), 2) Create sync logic (6 hours), 3) Build reporting dashboard (10 hours)")

# COMMAND ----------

# Example: Query projects
response = chat("Show me all projects and their current status")

# COMMAND ----------

# Example: Use a specific provider
response = chat("Analyze the complexity of integrating with Motion's API and suggest an implementation approach", 
                task_type="complex_reasoning",
                preferred_provider="anthropic")

# COMMAND ----------

# MAGIC %md
# MAGIC ## View Conversation History

# COMMAND ----------

# Get conversation context
context = state_manager.get_conversation(conversation.conversation_id)
print(f"Total messages: {len(context.messages)}")
print(f"Total tokens used: {context.total_tokens_used}")

# COMMAND ----------

# Display last few messages
for msg in context.messages[-3:]:
    print(f"\nTimestamp: {msg['timestamp']}")
    print(f"Request: {msg['request']['message']}")
    print(f"Response: {msg['response']['message'][:200]}...")
    print("-" * 50)