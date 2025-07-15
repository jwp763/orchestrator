# SuperClaude Comprehensive Guide for Claude Code

## Table of Contents

1. [Introduction & Philosophy](#introduction--philosophy)
2. [Installation & Setup](#installation--setup)
3. [Core Architecture](#core-architecture)
4. [Universal Flags & Token Management](#universal-flags--token-management)
5. [Cognitive Personas](#cognitive-personas)
6. [Command Reference](#command-reference)
7. [MCP Integration](#mcp-integration)
8. [Workflow Patterns](#workflow-patterns)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction & Philosophy

SuperClaude is a comprehensive configuration framework that transforms Claude Code into a specialized development environment. It provides 19 professional commands, 9 cognitive personas, and advanced MCP integration to enhance your development workflow.

### Core Philosophy

- **Evidence-Based Development**: All suggestions must cite authoritative sources
- **Token Efficiency**: Advanced compression modes for optimal performance
- **Professional Workflows**: Structured approaches to development tasks
- **Security-First**: Built-in security patterns and validation
- **Quality Standards**: Comprehensive validation and testing integration

### When to Use SuperClaude

✅ **Good fit for:**

- Teams wanting consistent AI assistance
- Projects needing specialized approaches
- Evidence-based development practices
- Token-conscious workflows
- Domain-specific expertise needs

❌ **May not suit:**

- Purely manual workflows
- Minimal configuration preferences
- Ad-hoc development styles
- Single-domain focus

---

## Installation & Setup

### Quick Installation

```bash
git clone https://github.com/NomenAK/SuperClaude.git
cd SuperClaude
./install.sh
```

### Advanced Installation Options

```bash
# Custom installation directory
./install.sh --dir /opt/claude

# Update existing installation
./install.sh --update

# Preview changes without applying
./install.sh --dry-run --verbose

# Skip confirmations (for automation)
./install.sh --force

# Log all operations
./install.sh --log install.log
```

### Installation Features

- **Update Mode**: Preserves customizations while updating
- **Dry Run**: Preview changes before applying
- **Smart Backups**: Automatic backup with timestamping
- **Clean Updates**: Removes obsolete files
- **Platform Detection**: Works with Linux, macOS, WSL
- **Progress Tracking**: Installation feedback

### Post-Installation Validation

```bash
/load                                    # Load project context
/analyze --code --think                  # Test analysis
/analyze --architecture --persona-architect  # Try personas
```

---

## Core Architecture

### Configuration Structure

```
~/.claude/
├── CLAUDE.md                    # Main configuration file
├── commands/                    # 19 specialized commands
│   ├── analyze.md
│   ├── build.md
│   ├── review.md
│   └── ...
├── commands/shared/            # Shared YAML resources
│   ├── superclaude-core.yml
│   ├── superclaude-personas.yml
│   ├── flag-inheritance.yml
│   └── ...
└── shared/                     # Core configuration files
    ├── superclaude-core.yml
    ├── superclaude-mcp.yml
    ├── superclaude-personas.yml
    └── superclaude-rules.yml
```

### Template System

SuperClaude uses an `@include` reference system for configuration management:

- **70% token reduction** through template reuse
- **Centralized updates** via shared YAML files
- **Reference validation** for integrity checking
- **Consistent behavior** across all commands

### Evidence-Based Standards

All responses must follow evidence-based practices:

- **Prohibited Language**: "best|optimal|faster|secure|better|improved|enhanced|always|never|guaranteed"
- **Required Language**: "may|could|potentially|typically|often|sometimes|measured|documented"
- **Evidence Requirements**: "testing confirms|metrics show|benchmarks prove|data indicates|documentation states"
- **Citations**: Official documentation required with version compatibility

---

## Universal Flags & Token Management

### Available on ALL Commands

#### 🧠 Thinking Depth Control

| Flag           | Description                                 | Token Usage |
| -------------- | ------------------------------------------- | ----------- |
| `--think`      | Multi-file analysis with expanded context   | ~4K tokens  |
| `--think-hard` | Architecture-level depth analysis           | ~10K tokens |
| `--ultrathink` | Critical system analysis with maximum depth | ~32K tokens |

#### 📦 Token Optimization

| Flag                         | Description                                         |
| ---------------------------- | --------------------------------------------------- |
| `--uc` / `--ultracompressed` | Activate UltraCompressed mode (70% token reduction) |

#### 🔧 MCP Server Control

| Flag        | Description                                   |
| ----------- | --------------------------------------------- |
| `--c7`      | Enable Context7 documentation lookup          |
| `--seq`     | Enable Sequential thinking analysis           |
| `--magic`   | Enable Magic UI component generation          |
| `--pup`     | Enable Puppeteer browser automation           |
| `--all-mcp` | Enable all MCP servers for maximum capability |
| `--no-mcp`  | Disable all MCP servers (native tools only)   |

#### 🔍 Analysis & Quality

| Flag           | Description                                            |
| -------------- | ------------------------------------------------------ |
| `--introspect` | Enable self-aware analysis with cognitive transparency |
| `--plan`       | Show detailed execution plan before running            |
| `--dry-run`    | Preview changes without execution                      |
| `--validate`   | Enhanced pre-execution safety checks                   |
| `--security`   | Security-focused analysis and validation               |
| `--strict`     | Zero-tolerance mode with enhanced validation           |

### UltraCompressed Mode

- **Activation**: `--uc` flag or natural language triggers ("compress", "concise", "brief")
- **Benefits**: 70% token reduction while preserving technical accuracy
- **Features**: Symbol-based communication, auto-generated legends, direct information only
- **Quality**: Maintains completeness and evidence-based claims

---

## Cognitive Personas

All personas are integrated as flags, available on every command:

### 🏗️ Architecture & Design

| Persona       | Flag                  | Best For                                                  |
| ------------- | --------------------- | --------------------------------------------------------- |
| **Architect** | `--persona-architect` | Systems thinking, scalability, patterns, long-term design |
| **Frontend**  | `--persona-frontend`  | UI/UX, accessibility, performance, user experience        |
| **Backend**   | `--persona-backend`   | APIs, databases, reliability, server architecture         |

### 🔍 Analysis & Quality

| Persona      | Flag                 | Best For                                              |
| ------------ | -------------------- | ----------------------------------------------------- |
| **Analyzer** | `--persona-analyzer` | Root cause analysis, evidence-based investigation     |
| **Security** | `--persona-security` | Threat modeling, vulnerability assessment, compliance |
| **QA**       | `--persona-qa`       | Testing strategies, edge cases, quality assurance     |

### 🛠️ Development & Improvement

| Persona         | Flag                    | Best For                                         |
| --------------- | ----------------------- | ------------------------------------------------ |
| **Refactorer**  | `--persona-refactorer`  | Code quality, maintainability, technical debt    |
| **Performance** | `--persona-performance` | Optimization, profiling, efficiency, bottlenecks |
| **Mentor**      | `--persona-mentor`      | Teaching, documentation, knowledge transfer      |

### Persona Characteristics

Each persona has:

- **Core Belief**: Fundamental philosophy driving decisions
- **Primary Question**: Key question they ask about problems
- **Decision Framework**: How they prioritize solutions
- **Success Metrics**: What they measure for success
- **MCP Preferences**: Which tools they prefer to use

---

## Command Reference

### 🛠️ Development Commands (3)

#### `/build` - Universal Project Builder

Build projects, features, and components using modern stack templates.

**Key Flags:**

- `--init` - Initialize new project with stack setup
- `--feature` - Implement feature using existing patterns
- `--tdd` - Test-driven development workflow
- `--react` - React with Vite, TypeScript, Router
- `--api` - Express.js API with TypeScript
- `--fullstack` - Complete React + Node.js + Docker

**Examples:**

```bash
/build --init --react --magic --tdd         # New React app with AI components
/build --feature "auth system" --tdd        # Feature with tests
/build --api --openapi --seq                # API with documentation
```

#### `/dev-setup` - Development Environment

Configure professional development environments with CI/CD and monitoring.

**Key Flags:**

- `--install` - Install and configure dependencies
- `--ci` - CI/CD pipeline configuration
- `--monitor` - Monitoring and observability setup
- `--docker` - Containerization setup

#### `/test` - Comprehensive Testing Framework

Create, run, and maintain testing strategies across the stack.

**Key Flags:**

- `--e2e` - End-to-end testing
- `--integration` - Integration testing
- `--coverage` - Generate comprehensive coverage analysis
- `--performance` - Performance testing

### 🔍 Analysis & Improvement Commands (5)

#### `/review` - AI-Powered Code Review

Comprehensive code review and quality analysis with evidence-based recommendations.

**Key Flags:**

- `--files` - Review specific files or directories
- `--commit` - Review changes in specified commit
- `--pr` - Review pull request changes
- `--quality` - Focus on code quality issues
- `--evidence` - Include sources and documentation

**Examples:**

```bash
/review --files src/auth.ts --persona-security    # Security-focused file review
/review --commit HEAD --quality --evidence        # Quality review with sources
/review --pr 123 --all --interactive             # Comprehensive PR review
```

#### `/analyze` - Multi-Dimensional Analysis

Comprehensive analysis of code, architecture, performance, and security.

**Key Flags:**

- `--code` - Code quality analysis
- `--architecture` - System design assessment
- `--profile` - Performance profiling
- `--deps` - Dependency analysis

#### `/troubleshoot` - Professional Debugging

Systematic debugging and issue resolution.

**Key Flags:**

- `--investigate` - Systematic issue analysis
- `--five-whys` - Root cause analysis
- `--prod` - Production debugging
- `--fix` - Complete resolution

#### `/improve` - Enhancement & Optimization

Evidence-based improvements with measurable outcomes.

**Key Flags:**

- `--quality` - Code structure improvements
- `--performance` - Performance optimization
- `--accessibility` - Accessibility improvements
- `--threshold` - Quality target percentage

#### `/explain` - Technical Documentation

Generate comprehensive explanations and documentation.

**Key Flags:**

- `--depth` - Complexity level (ELI5|beginner|intermediate|expert)
- `--visual` - Include diagrams
- `--api` - API documentation
- `--tutorial` - Learning tutorials

### ⚙️ Operations Commands (6)

#### `/deploy` - Application Deployment

Safe deployment with rollback capabilities.

**Key Flags:**

- `--env` - Target environment (dev|staging|prod)
- `--canary` - Canary deployment
- `--rollback` - Rollback to previous
- `--monitor` - Post-deployment monitoring

#### `/scan` - Security & Validation

Comprehensive security auditing and compliance.

**Key Flags:**

- `--security` - Security analysis
- `--owasp` - OWASP Top 10 compliance
- `--deps` - Dependency security scan
- `--compliance` - Regulatory compliance

#### `/migrate` - Database & Code Migration

Safe migrations with rollback capabilities.

**Key Flags:**

- `--database` - Database migrations
- `--backup` - Create backup first
- `--rollback` - Rollback migration
- `--validate` - Data integrity checks

#### `/estimate` - Project Estimation

Professional estimation with risk assessment.

**Key Flags:**

- `--detailed` - Comprehensive breakdown
- `--agile` - Story point estimation
- `--risk` - Risk assessment
- `--timeline` - Timeline planning

#### `/cleanup` - Project Maintenance

Professional cleanup with safety validations.

**Key Flags:**

- `--code` - Remove dead code
- `--deps` - Remove unused dependencies
- `--all` - Comprehensive cleanup
- `--dry-run` - Preview cleanup

#### `/git` - Git Workflow Management

Professional Git operations with safety features.

**Key Flags:**

- `--commit` - Professional commit
- `--checkpoint` - Create checkpoint
- `--sync` - Remote synchronization
- `--pre-commit` - Setup pre-commit hooks

### 🎨 Design & Workflow Commands (5)

#### `/design` - System Architecture

Professional system design with specifications.

**Key Flags:**

- `--api` - REST/GraphQL design
- `--ddd` - Domain-driven design
- `--microservices` - Microservices architecture
- `--openapi` - OpenAPI specs

#### `/task` - Task Management

Complex feature management across sessions.

**Operations:**

- `/task:create [description]` - Create task with breakdown
- `/task:status [task-id]` - Check task progress
- `/task:resume [task-id]` - Resume work after break
- `/task:complete [task-id]` - Mark task as done

#### `/load` - Project Context Loading

Load and analyze project context.

**Key Flags:**

- `--depth` - Analysis depth (shallow|normal|deep)
- `--context` - Context preservation
- `--structure` - Project structure analysis

#### `/document` - Documentation Creation

Professional documentation in multiple formats.

**Key Flags:**

- `--api` - API documentation
- `--user` - User guides
- `--technical` - Developer docs
- `--interactive` - Interactive docs

#### `/spawn` - Specialized Agents

Spawn focused agents for parallel tasks.

**Key Flags:**

- `--task` - Define specific task
- `--parallel` - Concurrent execution
- `--collaborative` - Multi-agent work

---

## MCP Integration

### Available MCP Servers

#### Context7 (`--c7`)

- **Purpose**: Access to library documentation and official sources
- **Best For**: Research, documentation lookup, API references
- **Use Cases**: Learning new frameworks, API documentation, best practices

#### Sequential (`--seq`)

- **Purpose**: Multi-step reasoning and complex analysis
- **Best For**: Architecture decisions, debugging, complex problem-solving
- **Use Cases**: System design, root cause analysis, planning

#### Magic (`--magic`)

- **Purpose**: AI-generated UI components and interfaces
- **Best For**: Frontend development, rapid prototyping
- **Use Cases**: React components, UI mockups, interactive elements

#### Puppeteer (`--pup`)

- **Purpose**: Browser automation and testing
- **Best For**: E2E testing, UI validation, performance testing
- **Use Cases**: Test automation, accessibility testing, performance monitoring

### MCP Best Practices

1. **Progressive Use**: Start with Context7, add Sequential for complex analysis
2. **Combination Power**: Use multiple servers for comprehensive results
3. **Token Efficiency**: Disable unused servers with `--no-mcp` or specific `--no-c7`
4. **Quality Focus**: Magic for UI, Puppeteer for testing, Sequential for analysis

---

## Workflow Patterns

### 🚀 Professional Development Workflows

#### Full-Stack Development

```bash
/design --api --ddd --persona-architect        # Architecture design
/build --fullstack --tdd --magic              # Implementation
/test --coverage --e2e --pup                  # Quality assurance
/deploy --env staging --validate              # Deployment
```

#### Security-First Development

```bash
/scan --security --owasp --deps --persona-security  # Security audit
/analyze --security --forensic --seq                # Analysis
/improve --security --validate --strict             # Improvements
/test --security --coverage                         # Validation
```

#### Performance Optimization

```bash
/analyze --profile --deep --persona-performance     # Analysis
/troubleshoot --perf --investigate --pup           # Investigation
/improve --performance --iterate --threshold 90%    # Optimization
/test --performance --load                          # Validation
```

#### Quality Assurance

```bash
/review --quality --evidence --persona-qa          # Review
/improve --quality --refactor --strict             # Improvements
/scan --validate --quality                         # Validation
/test --coverage --mutation                        # Testing
```

### 📋 Task Management Workflows

#### Complex Feature Development

```bash
/task:create "Implement OAuth 2.0 authentication system"
/task:status oauth-task-id                         # Check progress
/design --api --ddd --persona-architect           # Architecture
/build --feature --tdd --seq                      # Implementation
/task:update oauth-task-id "Added JWT support"    # Update progress
/test --coverage --e2e --pup                      # Testing
/task:complete oauth-task-id                      # Complete
```

#### Debugging Session

```bash
/troubleshoot --investigate --prod --persona-analyzer  # Investigation
/analyze --profile --deep --seq                        # Analysis
/improve --performance --fix                           # Resolution
/test --integration --validate                         # Validation
```

### 🔒 Safety Workflows

#### Pre-Deployment Safety

```bash
/test --coverage --strict                          # Full testing
/scan --security --owasp --deps                   # Security scan
/scan --validate --quality                        # Quality validation
/deploy --env staging --plan                      # Staged deployment
```

#### Migration Safety

```bash
/migrate --database --dry-run                     # Preview changes
/git --checkpoint "before migration"              # Create checkpoint
/migrate --database --backup --validate           # Safe migration
```

---

## Best Practices

### 🎯 Command Selection Guidelines

#### When to Use Each Command

- **Analysis First**: Always start with `/analyze` or `/load` for new projects
- **Security Critical**: Use `/scan --security` before any deployment
- **Quality Focus**: Use `/review --quality --evidence` for code improvements
- **Performance Issues**: Use `/troubleshoot --perf` then `/improve --performance`
- **Documentation**: Use `/explain` with appropriate depth and persona

#### Flag Combination Best Practices

1. **Always validate risky operations**:

   ```bash
   /deploy --env prod --validate --plan
   /migrate --database --dry-run --backup
   ```

2. **Use personas for specialized expertise**:

   ```bash
   /analyze --architecture --persona-architect
   /scan --security --persona-security
   ```

3. **Combine MCP servers for maximum capability**:

   ```bash
   /build --react --magic --seq --c7
   /test --e2e --pup --coverage
   ```

4. **Progressive thinking for complex tasks**:
   ```bash
   /troubleshoot --investigate --think
   /design --microservices --think-hard
   /analyze --architecture --ultrathink
   ```

### 💡 Token Optimization Strategies

#### When to Use UltraCompressed Mode

- **Large codebases**: Use `--uc` for analysis of large projects
- **Batch operations**: Multiple commands in sequence
- **Documentation generation**: When creating extensive docs
- **Repetitive tasks**: Similar operations across multiple files

#### Token-Efficient Workflows

```bash
# Efficient analysis workflow
/analyze --code --uc --no-mcp
/improve --quality --uc
/test --coverage --uc

# Compressed documentation
/document --api --uc --c7
/explain --depth expert --uc
```

### 🛡️ Security Best Practices

#### Security-First Development

1. **Always scan before deployment**:

   ```bash
   /scan --security --owasp --deps
   ```

2. **Use security persona for sensitive operations**:

   ```bash
   /review --files auth/ --persona-security
   /analyze --code --persona-security --strict
   ```

3. **Validate all security improvements**:
   ```bash
   /improve --security --validate
   /scan --validate --security
   ```

### 📊 Quality Assurance Patterns

#### Evidence-Based Quality

1. **Always require evidence for improvements**:

   ```bash
   /review --quality --evidence
   /improve --quality --threshold 95%
   ```

2. **Use multiple validation layers**:

   ```bash
   /test --coverage --strict
   /scan --validate --quality
   /review --quality --evidence
   ```

3. **Document quality improvements**:
   ```bash
   /explain --depth expert --evidence
   /document --technical --quality
   ```

---

## Troubleshooting

### Common Issues and Solutions

#### Installation Problems

**Issue**: Installation fails with permission errors
**Solution**:

```bash
# Ensure you're installing to user directory
./install.sh --dir ~/.claude

# Check permissions
ls -la ~/.claude
```

**Issue**: MCP servers not working
**Solution**:

- SuperClaude doesn't include MCP servers
- Install them separately in Claude Code's MCP settings
- Use `--no-mcp` flag if servers aren't available

#### Command Execution Issues

**Issue**: Command not recognized
**Solution**:

```bash
# Verify installation
ls ~/.claude/commands/

# Check command syntax
/command --help
```

**Issue**: Unexpected behavior with personas
**Solution**:

```bash
# Use introspection mode for debugging
/analyze --introspect --persona-analyzer
/troubleshoot --introspect --seq
```

#### Performance Issues

**Issue**: High token usage
**Solution**:

```bash
# Use UltraCompressed mode
/analyze --uc --no-mcp

# Disable unnecessary MCP servers
/build --react --no-seq --no-pup
```

### Debug Workflows

#### Framework Debugging

```bash
# Debug SuperClaude behavior
/troubleshoot --introspect --seq
/analyze --introspect --persona-analyzer
/improve --introspect --uc
```

#### Performance Debugging

```bash
# Analyze performance issues
/analyze --profile --deep --persona-performance
/troubleshoot --perf --investigate --pup
/improve --performance --iterate --threshold 90%
```

### Getting Help

#### Resources

- **README.md**: Overview & installation
- **COMMANDS.md**: Complete command reference
- **GitHub Issues**: Bug reports & discussions
- **GitHub Discussions**: Community Q&A

#### Self-Diagnosis

```bash
# Check system status
/load --depth shallow --health

# Analyze current setup
/analyze --introspect --think

# Get command help
/command --help
```

---

## Conclusion

SuperClaude transforms Claude Code into a professional development environment with:

- **19 Specialized Commands** covering the complete development lifecycle
- **9 Cognitive Personas** for domain-specific expertise
- **Advanced MCP Integration** for enhanced capabilities
- **Evidence-Based Methodology** ensuring quality and reliability
- **Token Optimization** for efficient resource usage

### Next Steps

1. **Install SuperClaude** using the provided installation script
2. **Start with `/load`** to understand your project context
3. **Experiment with personas** to find your preferred approaches
4. **Build workflows** that match your development style
5. **Contribute back** to the community with improvements and feedback

### Key Takeaways

- Always start with analysis (`/analyze` or `/load`)
- Use personas for specialized expertise
- Validate risky operations with `--dry-run` or `--validate`
- Combine MCP servers for maximum capability
- Use `--uc` for token efficiency when needed
- Follow evidence-based practices for quality assurance

SuperClaude is designed to grow with your needs and adapt to your workflow. Start simple, experiment with advanced features, and build the development environment that works best for you.

---

_SuperClaude v2.0.1 - Professional development framework for Claude Code_

**Links:**

- [GitHub Repository](https://github.com/NomenAK/SuperClaude)
- [Discussions](https://github.com/NomenAK/SuperClaude/discussions)
- [Issues](https://github.com/NomenAK/SuperClaude/issues)
