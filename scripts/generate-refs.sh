#!/bin/bash
# Generate API Reference Documentation
# Auto-generates API tables from code

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔄 Generating API Reference Documentation"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Output file
OUTPUT_FILE="docs/reference/api-endpoints.md"
mkdir -p "$(dirname "$OUTPUT_FILE")"

# Start the markdown file
cat > "$OUTPUT_FILE" << 'EOF'
# API Endpoints Reference

This document is auto-generated from the codebase. Last updated: $(date)

## Table of Contents

- [Projects API](#projects-api)
- [Tasks API](#tasks-api)
- [Conversations API](#conversations-api)
- [Authentication](#authentication)
- [Health Check](#health-check)

---

EOF

# Function to extract route information from Python files
extract_routes() {
    local file=$1
    local section=$2
    
    echo "## $section" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Extract route decorators and their functions
    python3 << PYTHON_EOF >> "$OUTPUT_FILE"
import re
import ast

with open('$file', 'r') as f:
    content = f.read()

# Find all route decorators
route_pattern = r'@(router|app)\.(get|post|put|patch|delete|options)\s*\(\s*["\']([^"\']+)["\'](.*?)\)'
routes = re.finditer(route_pattern, content, re.MULTILINE | re.DOTALL)

print("| Method | Endpoint | Description | Request Body | Response |")
print("|--------|----------|-------------|--------------|----------|")

for match in routes:
    method = match.group(2).upper()
    endpoint = match.group(3)
    
    # Try to find the function definition after the decorator
    func_start = match.end()
    func_pattern = r'(async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[^:]+)?:\s*"""(.*?)"""'
    func_match = re.search(func_pattern, content[func_start:func_start+2000], re.DOTALL)
    
    if func_match:
        func_name = func_match.group(2)
        docstring = func_match.group(3).strip()
        # Extract first line of docstring as description
        description = docstring.split('\\n')[0] if docstring else 'No description'
    else:
        func_name = 'unknown'
        description = 'No description'
    
    # Try to extract request/response info from docstring
    request_body = '-'
    response = '-'
    
    if func_match and func_match.group(3):
        docstring = func_match.group(3)
        # Look for Args: or Request: section
        args_match = re.search(r'(Args|Request|Parameters):\s*\n(.*?)(?=\n\s*\n|\n\s*Returns:|\Z)', docstring, re.DOTALL)
        if args_match:
            request_body = args_match.group(2).strip().replace('\n', ' ')[:50] + '...' if len(args_match.group(2).strip()) > 50 else args_match.group(2).strip()
        
        # Look for Returns: section
        returns_match = re.search(r'Returns?:\s*\n?(.*?)(?=\n\s*\n|\Z)', docstring, re.DOTALL)
        if returns_match:
            response = returns_match.group(1).strip().replace('\n', ' ')[:50] + '...' if len(returns_match.group(1).strip()) > 50 else returns_match.group(1).strip()
    
    print(f"| {method} | \`{endpoint}\` | {description} | {request_body} | {response} |")

print("")
PYTHON_EOF
}

# Process each router file
echo -e "${YELLOW}Processing backend API routes...${NC}"

if [ -f "backend/src/api/routes/projects.py" ]; then
    extract_routes "backend/src/api/routes/projects.py" "Projects API"
fi

if [ -f "backend/src/api/routes/tasks.py" ]; then
    extract_routes "backend/src/api/routes/tasks.py" "Tasks API"
fi

if [ -f "backend/src/api/routes/conversations.py" ]; then
    extract_routes "backend/src/api/routes/conversations.py" "Conversations API"
fi

# Add authentication section
cat >> "$OUTPUT_FILE" << 'EOF'
## Authentication

Currently, the API does not require authentication for the MVP. Future versions will implement:

- JWT-based authentication
- API key management
- Role-based access control (RBAC)

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns service health status |

---

## Error Responses

All endpoints may return the following error responses:

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:

- Per-IP rate limiting
- Per-user rate limiting
- Endpoint-specific limits

EOF

echo -e "${GREEN}✅ API reference generated at: $OUTPUT_FILE${NC}"

# Also generate a models reference
MODELS_FILE="docs/reference/data-models.md"

cat > "$MODELS_FILE" << 'EOF'
# Data Models Reference

This document is auto-generated from the Pydantic models. Last updated: $(date)

## Table of Contents

- [Project Models](#project-models)
- [Task Models](#task-models)
- [Conversation Models](#conversation-models)
- [Agent Models](#agent-models)

---

EOF

# Function to extract Pydantic models
extract_models() {
    local file=$1
    local section=$2
    
    echo "## $section" >> "$MODELS_FILE"
    echo "" >> "$MODELS_FILE"
    
    python3 << PYTHON_EOF >> "$MODELS_FILE"
import re
import ast

with open('$file', 'r') as f:
    content = f.read()

# Parse the Python file
try:
    tree = ast.parse(content)
except:
    print("Failed to parse file")
    exit()

# Find all class definitions that inherit from BaseModel
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        # Check if it inherits from BaseModel or similar
        base_names = [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
        if any('Model' in name or 'Base' in name for name in base_names):
            print(f"### {node.name}")
            print("")
            
            # Get docstring
            docstring = ast.get_docstring(node)
            if docstring:
                print(docstring)
                print("")
            
            print("| Field | Type | Required | Description |")
            print("|-------|------|----------|-------------|")
            
            # Extract fields
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_name = item.target.id
                    
                    # Get type annotation
                    type_str = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else 'Unknown'
                    
                    # Check if required (no default value)
                    required = "Yes" if item.value is None else "No"
                    
                    # Try to get field description from comments or docstring
                    description = "-"
                    
                    print(f"| {field_name} | \`{type_str}\` | {required} | {description} |")
            
            print("")

PYTHON_EOF
}

# Process model files
echo -e "${YELLOW}Processing data models...${NC}"

if [ -f "backend/src/models/project.py" ]; then
    extract_models "backend/src/models/project.py" "Project Models"
fi

if [ -f "backend/src/models/task.py" ]; then
    extract_models "backend/src/models/task.py" "Task Models"
fi

if [ -f "backend/src/models/conversation.py" ]; then
    extract_models "backend/src/models/conversation.py" "Conversation Models"
fi

echo -e "${GREEN}✅ Data models reference generated at: $MODELS_FILE${NC}"

# Generate CLI commands reference
CLI_FILE="docs/reference/cli-commands.md"

cat > "$CLI_FILE" << 'EOF'
# CLI Commands Reference

## Orchestrator CLI

The orchestrator provides a command-line interface for managing projects and tasks.

### Installation

```bash
pip install databricks-orchestrator
```

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-v` | Show version |
| `--config` | `-c` | Config file path |
| `--verbose` | | Enable verbose output |

### Commands

#### Project Management

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator project create` | Create a new project | `orchestrator project create "My Project"` |
| `orchestrator project list` | List all projects | `orchestrator project list --status active` |
| `orchestrator project update` | Update project details | `orchestrator project update PROJECT_ID --name "New Name"` |
| `orchestrator project delete` | Delete a project | `orchestrator project delete PROJECT_ID` |

#### Task Management

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator task create` | Create a new task | `orchestrator task create --project PROJECT_ID "Task Title"` |
| `orchestrator task list` | List tasks | `orchestrator task list --project PROJECT_ID` |
| `orchestrator task update` | Update task | `orchestrator task update TASK_ID --status completed` |
| `orchestrator task assign` | Assign task to agent | `orchestrator task assign TASK_ID --agent planner` |

#### Agent Operations

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator agent list` | List available agents | `orchestrator agent list` |
| `orchestrator agent status` | Check agent status | `orchestrator agent status planner` |
| `orchestrator agent execute` | Execute agent on task | `orchestrator agent execute AGENT_ID TASK_ID` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCHESTRATOR_API_URL` | API endpoint URL | `http://localhost:8000` |
| `ORCHESTRATOR_CONFIG` | Config file path | `~/.orchestrator/config.yaml` |
| `ORCHESTRATOR_LOG_LEVEL` | Logging level | `INFO` |

EOF

echo -e "${GREEN}✅ CLI reference generated at: $CLI_FILE${NC}"
echo -e "${GREEN}✅ All reference documentation generated successfully!${NC}"