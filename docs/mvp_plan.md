## Comprehensive MVP Project Plan: Conversational Project & Task Manager

### **1. Project Overview & Guiding Principles**

This document outlines the plan for building a Minimum Viable Product (MVP) of an intelligent project management tool. The core of this system is a conversational AI agent that assists a user in defining, structuring, and refining projects and their associated tasks.

The user interacts with the system through a simple web-based GUI. All interactions are conversational; the user provides plain-text requests, and the AI agent returns structured "patches" or "diffs" representing proposed changes. This "diff-first" approach is a foundational principle, ensuring that every change is explicit, reviewable, and auditable.

#### **1.1. Core User Experience**

1.  **Project Scaffolding**: A user initiates a new project with a high-level goal (e.g., "Build a new user authentication flow"). The AI agent proposes an initial breakdown of this goal into a small, manageable number of high-level tasks. This proposal is presented as a diff.
2.  **Iterative Refinement**: The user converses with the agent to refine this initial plan ("Combine the first two tasks," "Add a task for documentation"). Each new instruction results in a new diff, which is applied to the proposal.
3.  **Approval & Task Decomposition**: Once satisfied, the user accepts the high-level project structure. They can then select any individual task and, through a separate, focused conversation, break it down into smaller, more granular sub-tasks. This decomposition process is recursive.
4.  **Visualization**: Throughout this process, the GUI provides a clear, text-based, hierarchical visualization of the project, allowing the user to expand and collapse sections to see the current state of the plan.

#### **1.2. Key Architectural Principles**

*   **Diff-First Interaction**: The AI agent **never** outputs a full project or task object after the initial creation. It **always** outputs a `Patch` object that describes the requested `create`, `update`, or `delete` operations. The very first plan is simply a `Patch` against an empty project. This simplifies validation, makes changes explicit, and provides a natural audit trail.
*   **Separation of Concerns (Project vs. Task Mode)**: The AI agent operates in two distinct modes to ensure focused and relevant output.
    *   **Project Mode**: Used for the initial project scaffolding. The agent's focus is on high-level planning, breaking a large vision into coherent, top-level tasks (e.g., milestones with a 1-2 week horizon). It reasons about dependencies and overall structure.
    *   **Task Mode**: Used for decomposing an existing task into sub-tasks. The agent's focus is on granular detail, technical sequencing, and defining clear acceptance criteria. The broader project context is provided as a constraint, but the agent's primary goal is to flesh out the single task it was given.
*   **Storage Abstraction**: The application logic will be decoupled from the physical storage layer. All database operations will go through a defined interface (a repository pattern). This allows the initial SQL implementation to be swapped for Delta Lake or another backend in the future without rewriting the core application.

#### **1.3. Core Concepts & Data Hierarchy**

*   **Project**: The top-level container for work. It has a title, a summary, and a collection of root-level tasks.
*   **Task**: A unit of work within a project. Tasks can be nested to create a hierarchy (sub-tasks). A task has attributes like a title, description, status, and a list of its own sub-tasks.
*   **Patch**: A Pydantic object that represents a set of changes. It contains the operation (`create`, `update`, `delete`), the target ID, and the body of the changes.

---

### **2. System Architecture**

The MVP will consist of three main components running locally:

1.  **Front-End (Browser)**: A single-page application built with standard HTML, CSS, and vanilla JavaScript. It will be located in a new top-level `frontend/` directory.
2.  **Back-End (Python)**: A lightweight web server using **FastAPI**. The main application entrypoint will be `src/main.py`. It will expose a simple REST API, with routing defined in `src/orchestration/api.py`. The core application logic will reside in `src/orchestration/` to orchestrate calls between the AI agent and the storage layer.
3.  **Storage Layer (SQL)**: A local **SQLite** database, accessed via a **SQLAlchemy** ORM implementation defined in `src/storage/sql_implementation.py`. This will persist all project and task data.

---

### **3. Detailed Implementation Plan**

This plan is broken into four sequential phases. Each phase builds upon the last, resulting in a testable, functional increment.

#### **Phase 1: Core Schemas & Storage Foundation (Est. 4-5 hours)**

*Goal: Establish the data structures and a durable, abstracted persistence layer.*

*   **Task 1.1: Define Core Pydantic Schemas.**
    *   Create `src/models/schemas.py`.
    *   Define `Task` model: `id`, `project_id`, `parent_task_id` (for nesting), `title`, `description`, `status`.
    *   Define `Project` model: `id`, `title`, `summary`.
    *   Note: For the database, these will translate to SQLAlchemy models with relationships in the same file or a related one within `src/models`.

*   **Task 1.2: Define Patch Schemas.**
    *   In `src/models/schemas.py`, define the `Op` enum (`create`, `update`, `delete`).
    *   Define `TaskPatch` model: `op`, `task_id`, `body` (containing optional `Task` fields).
    *   Define `ProjectPatch` model: `project_id`, `base_version`, `meta_updates` (for title/summary), and a list of `TaskPatch` objects.

*   **Task 1.3: Design the Storage Interface (Repository Pattern).**
    *   Create `src/storage/interface.py`.
    *   Define an abstract base class `StorageInterface` with methods like:
        *   `get_project(project_id: str) -> Project`
        *   `get_task_tree(task_id: str) -> Task` (recursively fetches sub-tasks)
        *   `create_project(title: str) -> Project`
        *   `apply_project_patch(patch: ProjectPatch)`
        *   `apply_task_patch(patch: TaskPatch)`

*   **Task 1.4: Implement the SQL Storage Layer.**
    *   Create `src/storage/sql_implementation.py`.
    *   Implement the `SQLStorage` class, inheriting from `StorageInterface`.
    *   Use SQLAlchemy to define `Project` and `Task` tables, including a self-referential relationship for task nesting.
    *   Implement the interface methods using SQLAlchemy sessions to interact with the SQLite database. Ensure `apply_*_patch` methods handle operations transactionally.

#### **Phase 2: The Conversational Diff Agent (Est. 3-4 hours)**

*Goal: Create the AI "brain" that powers the conversational interaction.*

*   **Task 2.1: Implement the Diff Agent.**
    *   Create `src/agent/diff_agent.py`.
    *   Define a `DiffAgent` class. It will be initialized with an AI provider client (e.g., OpenAI, Anthropic).
    *   Create a primary method: `get_diff(mode: str, context: dict, user_message: str) -> Union[ProjectPatch, TaskPatch]`.

*   **Task 2.2: Develop the "Project Mode" Prompt Template.**
    *   The prompt must instruct the AI to act as a high-level project planner.
    *   **Key Instructions:**
        *   "Your goal is to break the user's request into a maximum of **6** high-level tasks."
        *   "Return ONLY a valid JSON object conforming to the `ProjectPatch` schema."
        *   "When creating a new project, all tasks should have the `op: create`."
        *   "Focus on deliverables, not granular steps."
    *   The prompt will be dynamically populated with the current project state (if any) and the user's message.

*   **Task 2.3: Develop the "Task Mode" Prompt Template.**
    *   The prompt must instruct the AI to act as a detailed task decomposer.
    *   **Key Instructions:**
        *   "Your goal is to break the provided task into smaller, actionable sub-tasks."
        *   "Return ONLY a valid JSON object conforming to the `TaskPatch` schema."
        *   "All generated sub-tasks are children of the task with ID: `{task_id}`."
        *   "Focus on technical steps, acceptance criteria, and details."
    *   The prompt will be populated with the context of the parent task and the broader project, plus the user's message.

*   **Task 2.4: Implement Agent Logic.**
    *   The `get_diff` method will:
        1.  Select the appropriate prompt template based on `mode`.
        2.  Format the prompt with the `context` and `user_message`.
        3.  Call the LLM API.
        4.  Parse the returned JSON string and validate it against the corresponding Pydantic `Patch` schema.
        5.  Implement a simple retry mechanism if JSON validation fails.

#### **Phase 3: The Backend API & Orchestration (Est. 3 hours)**

*Goal: Expose the core logic through a web server and orchestrate the components.*

*   **Task 3.1: Set up FastAPI Application.**
    *   Create `src/main.py` to initialize and run the FastAPI app.
    *   Create `src/orchestration/api.py` to define the FastAPI routers.
    *   In `src/main.py`, initialize the `SQLStorage` and `DiffAgent` instances and include the router from `src/orchestration/api.py`.

*   **Task 3.2: Create Orchestration Logic.**
    *   Create `src/orchestration/chat_service.py`.
    *   This service will contain the business logic, taking a user message and project/task context, calling the `DiffAgent`, and returning the patch. This keeps the API layer thin.

*   **Task 3.3: Define API Endpoints.**
    *   In `src/orchestration/api.py`:
    *   `POST /projects`: Creates a new empty project. Returns the new `Project` object.
    *   `GET /projects/{project_id}`: Returns the full project object with its hierarchy of tasks.
    *   `POST /projects/{project_id}/chat`:
        *   Accepts a user message.
        *   Calls the chat service to get a `ProjectPatch`.
        *   Returns the generated `ProjectPatch` JSON.
    *   `POST /tasks/{task_id}/chat`:
        *   Calls the chat service to get a `TaskPatch`.
        *   Returns the generated `TaskPatch` JSON.
    *   `POST /apply-patch`:
        *   Accepts either a `ProjectPatch` or a `TaskPatch`.
        *   Calls the appropriate `storage.apply_*_patch` method.
        *   Returns a success/failure status.

#### **Phase 4: The GUI Front-End (Est. 4-5 hours)**

*Goal: Build the user-facing interface to interact with the system.*

*   **Task 4.1: Create the HTML Structure.**
    *   Create a new `frontend/` directory at the project root.
    *   Inside `frontend/`, create `index.html`.
    *   Structure the HTML with three main divs:
        1.  `#project-view`: To display the current project hierarchy.
        2.  `#chat-interface`: To contain the chat input field, a "mode" indicator (Project/Task), and a submit button.
        3.  `#diff-view`: To display the JSON diff received from the agent, along with "Accept" and "Discard" buttons.

*   **Task 4.2: Implement the Rendering Logic.**
    *   Create `frontend/ui.js`.
    *   Write a `renderProject(projectData)` function that recursively builds the project and task hierarchy using nested `<ul>` and `<li>` elements. Make tasks collapsible.
    *   Write a `renderDiff(patchData)` function that pretty-prints the JSON patch in the `#diff-view` container.

*   **Task 4.3: Implement the API Communication Logic.**
    *   Create `frontend/api.js`.
    *   Write JavaScript `async` functions to wrap `fetch` calls for each backend endpoint (`createProject`, `getProject`, `postChatMessage`, `applyPatch`).

*   **Task 4.4: Wire Up the User Interaction.**
    *   Create `frontend/main.js`.
    *   On page load, prompt the user to create or load a project.
    *   Handle the chat submission:
        1.  Get the user's text.
        2.  Determine the current mode (are we editing the project or a specific task?).
        3.  Call the appropriate `postChatMessage` API function.
        4.  Render the returned diff using `renderDiff`.
    *   Handle the "Accept" button click:
        1.  Call the `applyPatch` API function with the current diff.
        2.  On success, clear the diff view and re-fetch/re-render the entire project to show the updated state.