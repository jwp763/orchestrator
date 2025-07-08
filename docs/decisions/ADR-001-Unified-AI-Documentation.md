# ADR-001: Unified AI Documentation Strategy

## Status
Accepted

## Context
This project is heavily reliant on AI coding agents for development and maintenance. To ensure that these agents can work effectively and consistently, we need a clear and unified documentation strategy that they can easily understand and use. The primary AI agents to support are Google Gemini CLI, Anthropic's Claude Code, and OpenAI's Codex.

## Decision
We will adopt a hybrid, hierarchical documentation strategy with a single source of truth for core AI context.

1.  **Master Context File (`PROJECT.md`):** A single `PROJECT.md` file at the root of the repository will serve as the primary source of truth for high-level AI context. This file will contain the project's mission, tech stack, coding standards, and pointers to more detailed documentation.

2.  **Symbolic Links for Native Tooling:** To ensure each AI tool natively discovers its expected context file, we will create symbolic links from `PROJECT.md` to `GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`.

3.  **Structured Task Management (`.ai/tasks/`):** For detailed task management, we will use YAML files in the `.ai/tasks/` directory. This allows for structured definitions of tasks, including dependencies, status, and other metadata, which is more robust than managing complex plans in Markdown.

4.  **Detailed Context (`.ai/context/` and `docs/`):** More detailed documentation, such as architecture diagrams, coding standards, and Architecture Decision Records (ADRs), will be stored in the `.ai/context/` and `docs/` directories. The `PROJECT.md` file will link to these documents.

## Consequences
- **Pros:**
    - **Consistency:** All AI agents work from the same core context, ensuring consistent behavior.
    - **Maintainability:** We only need to update the `PROJECT.md` file and the YAML task files, rather than managing multiple, separate documentation sources.
    - **Flexibility:** The hybrid approach allows us to use Markdown for human-readable context and YAML for machine-parsable tasks.
    - **Extensibility:** This structure can be easily extended to support new AI tools in the future.

- **Cons:**
    - **Symbolic Links:** Requires an environment that supports symbolic links. This is standard in most development environments but could be a consideration.
    - **Discipline:** Requires the discipline to keep the documentation up-to-date.
