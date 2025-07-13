# Documentation Standards

This document defines the standards and guidelines for maintaining documentation in the Databricks Orchestrator project.

## Table of Contents

- [File Organization](#file-organization)
- [Document Structure](#document-structure)
- [Writing Style](#writing-style)
- [File Size Guidelines](#file-size-guidelines)
- [Required Sections](#required-sections)
- [Templates](#templates)
- [Maintenance](#maintenance)

## File Organization

### Directory Structure

```
docs/
├── README.md                 # Documentation index
├── DOCUMENTATION_STANDARDS.md # This file
├── architecture/             # System architecture docs
│   ├── overview.md
│   ├── components.md
│   └── data-flow.md
├── development/              # Development guides
│   ├── setup.md
│   └── contributing.md
├── testing/                  # Testing documentation
│   ├── overview.md
│   ├── backend-guide.md
│   ├── frontend-guide.md
│   └── troubleshooting.md
├── deployment/               # Deployment guides
│   └── guide.md
├── reference/                # API and CLI reference
│   ├── api-endpoints.md
│   ├── data-models.md
│   ├── cli-commands.md
│   └── configuration.md
├── planning/                 # Project planning docs
│   ├── mvp-overview.md
│   ├── phase-1.md
│   └── roadmap.md
└── decisions/                # Architecture Decision Records
    └── adr-template.md
```

### Naming Conventions

- Use lowercase with hyphens: `backend-guide.md`
- Be descriptive but concise: `api-endpoints.md` not `api.md`
- Use `.md` extension for all documentation
- Number ADRs: `001-use-fastapi.md`

## Document Structure

### Required Elements

Every documentation file MUST include:

1. **Title** (H1) - Clear, descriptive title
2. **Purpose Statement** - One paragraph explaining what the document covers
3. **Table of Contents** - For files > 300 lines
4. **Sections** - Logical organization with headers
5. **Related Links** - Links to related documentation

### Header Hierarchy

```markdown
# Document Title (H1 - One per document)

Brief description of what this document covers.

## Table of Contents (H2 - If needed)

## Major Section (H2)

### Subsection (H3)

#### Detail Level (H4)

##### Fine Detail (H5 - Avoid if possible)
```

## Writing Style

### General Guidelines

- **Be Concise**: Get to the point quickly
- **Use Active Voice**: "The system processes..." not "Processing is done by..."
- **Present Tense**: "The API returns..." not "The API will return..."
- **Second Person**: Address the reader as "you"
- **Examples**: Include code examples for technical concepts

### Code Examples

```markdown
Always include language identifier:
​```python
def example():
    return "Hello"
​```

Include context and explanation:
# Good: Explains what and why
​```python
# Configure retry logic for resilient API calls
retry_config = {
    "max_attempts": 3,
    "backoff_factor": 2
}
​```
```

### Lists and Tables

Use tables for structured data:

| Feature | Status | Notes |
|---------|--------|-------|
| Auth | ✅ | JWT-based |
| RBAC | 🚧 | In progress |

Use lists for sequential steps or unordered items:

1. Install dependencies
2. Configure environment
3. Run the application

## File Size Guidelines

### Size Limits

- **Ideal**: < 10KB (approx. 300 lines)
- **Acceptable**: < 20KB (approx. 600 lines)
- **Requires Split**: > 20KB

### When to Split Documents

Split large documents when:
- File exceeds 600 lines
- Multiple distinct topics are covered
- Different audiences (dev vs. ops)

### How to Split

1. Identify logical sections
2. Create new files for each major topic
3. Update original file with links
4. Add navigation between related docs

## Required Sections

### For README Files

```markdown
# Project/Component Name

Brief description (1-2 sentences).

## Overview
What this component does and why it exists.

## Installation
Step-by-step installation instructions.

## Usage
Basic usage examples.

## Configuration
Configuration options and examples.

## Development
Development setup and guidelines.

## Testing
How to run tests.

## Troubleshooting
Common issues and solutions.

## Related Documentation
Links to related docs.
```

### For API Documentation

```markdown
# API Name

## Overview
Purpose and capabilities.

## Authentication
How to authenticate.

## Endpoints
Detailed endpoint documentation.

## Data Models
Request/response schemas.

## Error Handling
Error codes and meanings.

## Rate Limiting
Limits and best practices.

## Examples
Complete usage examples.
```

### For Guides

```markdown
# Guide Title

## Prerequisites
What you need before starting.

## Overview
What you'll learn/accomplish.

## Steps
Numbered steps with explanations.

## Verification
How to verify success.

## Troubleshooting
Common issues and fixes.

## Next Steps
Where to go from here.
```

## Templates

### Architecture Decision Record (ADR)

```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-YYY]

## Context
What is the issue we're seeing that motivates this decision?

## Decision
What is the change that we're proposing/doing?

## Consequences
What becomes easier or harder because of this change?

## Alternatives Considered
What other options were evaluated?
```

### Feature Documentation

```markdown
# Feature Name

## Overview
What this feature does.

## Use Cases
- Use case 1
- Use case 2

## Implementation
How it works under the hood.

## Configuration
Available options.

## API Reference
Related endpoints.

## Examples
Code examples.

## Limitations
Known limitations.

## Future Enhancements
Planned improvements.
```

## Maintenance

### Regular Reviews

- **Monthly**: Check for outdated information
- **Quarterly**: Review structure and organization
- **On Major Release**: Update all affected docs

### Documentation Checklist

Before merging documentation:

- [ ] Spell check completed
- [ ] Links verified (run `scripts/doc-check.sh`)
- [ ] Code examples tested
- [ ] TOC updated (if applicable)
- [ ] Related docs updated
- [ ] Follows size guidelines
- [ ] Reviewed by team member

### Automated Checks

Run before committing:

```bash
# Check documentation quality
./scripts/doc-check.sh

# Generate/update references
./scripts/generate-refs.sh

# Update old links
./scripts/update-links.py --dry-run
```

### Version Control

- Use meaningful commit messages
- Reference issues/PRs in commits
- Keep documentation in sync with code
- Tag documentation versions with releases

## Tools and Automation

### Available Scripts

1. **doc-check.sh** - Quality checks
   - Link validation
   - File size checks
   - TODO detection
   - Format validation

2. **generate-refs.sh** - Auto-generation
   - API endpoint tables
   - Data model documentation
   - CLI command reference

3. **update-links.py** - Link maintenance
   - Batch update old paths
   - Custom path mappings
   - Dry-run mode

### CI/CD Integration

All documentation changes trigger:
- Link checking
- Size validation
- Format verification
- Spell checking (if configured)

## Contributing

When contributing documentation:

1. Follow these standards
2. Run quality checks locally
3. Update related documentation
4. Include in PR description:
   - What documentation changed
   - Why the change was needed
   - Any new sections added

## Questions?

For questions about documentation standards:
- Check existing examples in `docs/`
- Ask in PR reviews
- Create an issue for clarification