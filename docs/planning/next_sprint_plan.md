# Next Sprint Plan: Chat Panel with Patch Suggestion/Acceptance Flow

## Overview

This document outlines the implementation plan for a conversational UI that enables users to iteratively refine projects through a chat interface with structured patch suggestions. The system provides a tight feedback loop between three surfaces:

- **Chat input**: Where users express intent in natural language
- **Suggestion tray**: Where AI proposes structured changes as patches
- **Project canvas**: Where the currently-accepted state is rendered and editable

## Core Design Principles

1. **Patches, not mutations**: All AI responses are candidate patches, never immediate mutations
2. **Auditable history**: Store both raw conversation and every accepted patch as first-class records
3. **Immediate reactivity**: UI updates optimistically with rollback on conflicts
4. **Full context preservation**: Conversations and artifacts are preserved for future reference
5. **Progressive disclosure**: Simple defaults with advanced controls available when needed

## Data Contracts

### 1. SendMessageRequest (Chat Panel → Backend)

```json
{
  "project_id": "UUID",
  "text": "string",
  "controls": {
    "model": "gpt-4o",
    "intent": "auto" | "plan" | "decompose" | "edit_fields",
    "max_tasks": 6,
    "depth_limit": 1,
    "fields_to_edit": ["title", "description"],
    "input_type": "idea" | "transcript" | "requirements",
    "temperature": 0.7,
    "use_memory": true
  },
  "attachment_ids": ["UUID"]
}
```

### 2. Message (Conversation Table)

```json
{
  "id": "UUID",
  "project_id": "UUID",
  "role": "user" | "assistant",
  "content": "string",
  "controls": "object",
  "suggestions": ["Patch"],
  "created_at": "ISO-8601"
}
```

### 3. Patch (Existing Schema)

```json
{
  "op": "create" | "update" | "delete",
  "path": "/tasks/123/title",
  "value": "Implement login flow"
}
```

### 4. ApplyPatchRequest (UI → Backend)

```json
{
  "project_id": "UUID",
  "patch_id": "UUID",
  "source_message_id": "UUID"
}
```

### 5. PatchHistory (Audit Trail)

```json
{
  "id": "UUID",
  "project_id": "UUID",
  "patch_json": "object",
  "applied_by": "user" | "bulk-accept",
  "applied_at": "ISO-8601",
  "supersedes": "UUID"
}
```

## Chat Panel Controls

### Control Bar (High-Frequency)

- **Model/Provider Selector**: OpenAI GPT-4o, Claude 3, Local LLM
- **Max Top-Level Tasks**: Spin-box (1-10) - simplifies generation
- **Milestones Toggle**: Whether to auto-generate milestone tasks
- **Depth Limit**: 1 = tasks only, 2 = tasks + subtasks

### Intent Selector (Dropdown)

- **Auto**: Let OrchestratorAgent decide
- **New project plan**: Initial project creation
- **Break down selected task**: Task decomposition
- **Edit field(s) on selected item**: Field editing
- **Summarise/reflect**: Project analysis

### Field Scope (Multi-select, appears for "Edit field(s)")

- Title, Description, Priority, Status, Estimated Time, Tags
- "All fields" checkbox (default)

### Input Type (Small dropdown)

- **Idea/Prompt** (default)
- **Meeting transcript**
- **Requirements doc**
- **Screenshot/Image** (future: OCR)
- **Code snippet**

### Attachments

- Drag-and-drop zone + Upload icon
- Accept text files, PDFs, images
- Show inline chips with file name + type icon

### Advanced Drawer (Behind ⚙︎ icon)

- **Temperature/Creativity**: Slider (0.0-1.0)
- **System prompt override**: Textarea for power users
- **Use project memory**: Toggle for conversation + vector recall
- **Return reasoning**: Toggle for explanation of patch decisions

### Quick Presets (Optional)

- Chips: "Brainstorm", "Refine", "Split Tasks", "Summarise"
- Pre-configured bundles of Generation + Intent settings

## Message/Patch Lifecycle

### Step 0: User Input

User types text, tweaks controls → POST /messages

### Step 1: Message Persistence

Server saves user Message (role=user) and enqueues OrchestratorAgent job

### Step 2: Agent Processing

Agent runs, produces Patch[] + rationale → stores assistant Message (role=assistant, suggestions=Patch[])

### Step 3: Real-time Updates

Backend pushes assistant Message over WebSocket "project/{id}"

### Step 4: UI Rendering

Frontend receives message, renders:

- Chat bubble with rationale (if any)
- Suggestion Tray: one card per Patch (sortable chips)

### Step 5: User Actions per Patch

- **Accept**: POST /patches (ApplyPatchRequest)
- **Edit**: Opens inline JSON/YAML diff editor, then Accept
- **Reject**: Removes card (no server call)
- **Bulk-accept**: Single ApplyPatchRequest with array of IDs

### Step 6: Patch Application

Server transaction:

- Validates Patch against current project state
- Applies via ProjectService/TaskService
- Writes PatchHistory rows
- Commits and broadcasts "patch-applied" event

### Step 7: UI State Updates

Frontend on "patch-applied":

- Updates project canvas state (optimistic if desired)
- Marks suggestion card as "accepted" (greyed out, check-mark)
- Scrolls canvas to changed entity and pulse-highlights for 1.5s

### Step 8: Conversation Preservation

Conversation view remains untouched for audit and future context retrieval

## UI Component Architecture

### React Component Tree

```
ChatPanel
├── InputArea (textarea + controls)
├── ControlBar (model, intent, etc.)
├── AttachmentZone
└── SuggestionTray ✱ shown if last assistant Message contains suggestions
    ├── SuggestionCard (one per Patch)
    │   ├── DiffPreview (hover/expand)
    │   └── Accept ▯ Edit ▯ Reject buttons
    └── BulkActionsBar (Accept All, Reject All)

ProjectCanvas
└── TaskTree, ProjectMeta, etc. (subscribed to WebSocket "patch-applied")
```

### Client-side State (Zustand/Redux)

```javascript
{
  conversation: Map<messageId, Message>,
  suggestions: Map<patchId, PatchCardState>,   // pending/accepted/rejected/error
  project: ProjectSnapshot                      // the tree in the canvas
}
```

### State Machine

```
STATE: idle → sending → waiting → suggestion-ready → applying-patch
ACTIONS: send, receive_suggestions, accept, reject, apply_success, apply_error
```

## Agent Architecture

### OrchestratorAgent (Entry Point)

- Classifies user message (plan vs. decompose vs. edit vs. chit-chat)
- Forwards to appropriate specialist agent
- Packages result as suggestions
- All classification + routing rules in code for <1s latency

### Specialist Agents

- **PlannerAgent**: Transforms raw idea into ProjectPatch + TaskPatches (already implemented)
- **DecomposerAgent**: Given large task, returns TaskPatches (children) + meta TaskPatch
- **FieldEditorAgent**: Focused on editing single field; simpler prompt, better precision

### Agent Contracts

- Never mutate "source of truth" directly
- Always emit patches for user approval
- Include reasoning when requested
- Support context-based configuration overrides

## Backend Services

### New Tables Required

#### Conversation Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    role VARCHAR(20) NOT NULL,  -- 'user' | 'assistant'
    content TEXT NOT NULL,
    controls JSONB,             -- for user messages
    suggestions JSONB,          -- for assistant messages
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Artifact Table

```sql
CREATE TABLE artifacts (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    content_blob BYTEA,
    semantic_type VARCHAR(50),  -- 'transcript' | 'requirements' | 'image'
    vector_id UUID,            -- for similarity search
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### PatchHistory Table

```sql
CREATE TABLE patch_history (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    patch_json JSONB NOT NULL,
    applied_by VARCHAR(50) NOT NULL,  -- 'user' | 'bulk-accept'
    applied_at TIMESTAMP DEFAULT NOW(),
    supersedes UUID REFERENCES patch_history(id),
    source_message_id UUID REFERENCES conversations(id)
);
```

### API Endpoints

#### POST /messages

- Accepts SendMessageRequest
- Saves user message
- Enqueues agent processing
- Returns message ID

#### GET /messages/{project_id}

- Returns conversation history
- Includes suggestions for assistant messages
- Supports pagination

#### POST /patches

- Accepts ApplyPatchRequest
- Validates patch against current state
- Applies transactionally
- Broadcasts over WebSocket

#### DELETE /patches/{history_id}

- Reverts applied patch
- Applies inverse patch
- Updates history

### ApplyPatchService

- Starts DB transaction
- Validates patch against current project state
- Calls underlying repositories (ProjectService/TaskService)
- Writes PatchHistory
- Commits and broadcasts events

### WebSocket Events

- Channel: "project/{id}"
- Events: "patch-applied", "message-received", "user-typing"
- Keeps all connected tabs in sync

## Edge Cases & Error Handling

### Stale Patches

- Backend returns 409 Conflict
- UI tags suggestion "Outdated (re-generate)"
- User can refresh suggestions

### Multiple Users

- WebSocket events keep every tab in sync
- Optimistic updates roll back if 409 arrives
- Last-write-wins with conflict notification

### Undo Operations

- "Revert" button calls DELETE /patches/{history_id}
- Applies inverse patch stored in History
- Maintains full audit trail

### Agent Failures

- JSONParsingError: Invalid JSON from LLM
- ValidationError: Data fails Pydantic validation
- AgentError: General agent failures
- All include retry logic with exponential backoff

## Implementation Phases

### Phase 1: MVP Chat Panel (Week 1-2)

**Goal**: Basic chat with patch suggestions

**Deliverables**:

- ChatPanel React component with basic controls
- POST /messages endpoint
- Hard-coded OrchestratorAgent → PlannerAgent flow
- SuggestionTray with Accept/Reject (no Edit)
- ApplyPatch backend (no WebSocket yet)

**Success Criteria**:

- User can type project idea
- AI generates project + task patches
- User can accept/reject suggestions
- Project canvas updates after acceptance

### Phase 2: Enhanced Controls (Week 3)

**Goal**: Full control panel functionality

**Deliverables**:

- All control bar options implemented
- Intent selector with proper routing
- Field scope for editing
- Input type classification
- Attachment upload system

**Success Criteria**:

- User can control generation parameters
- Different input types handled appropriately
- Attachments stored and referenced

### Phase 3: Real-time & Editing (Week 4)

**Goal**: Live updates and patch editing

**Deliverables**:

- WebSocket integration
- Patch editing interface
- Bulk operations
- Optimistic updates with rollback

**Success Criteria**:

- Multiple users see updates in real-time
- Patches can be edited before acceptance
- Bulk accept/reject works smoothly

### Phase 4: Advanced Features (Week 5-6)

**Goal**: Full conversational experience

**Deliverables**:

- DecomposerAgent for task breakdown
- FieldEditorAgent for targeted edits
- Advanced drawer with all options
- Conversation history and replay
- Undo/redo functionality

**Success Criteria**:

- Complex multi-turn conversations work
- Task decomposition flows naturally
- Full audit trail maintained
- Power user features accessible

### Phase 5: Vector & Recall (Week 7-8)

**Goal**: Long-term memory and context

**Deliverables**:

- Vector embedding for conversations
- Artifact indexing and search
- Context-aware agent responses
- Project memory toggle

**Success Criteria**:

- Agents reference past conversations
- Uploaded documents influence responses
- Context remains relevant over time

## Testing Strategy

### Unit Tests

- React components with React Testing Library
- Agent classes with mocked LLM responses
- Service layer with isolated database

### Integration Tests

- Full message → patch → apply flow
- WebSocket event propagation
- Multi-user scenarios

### E2E Tests

- Complete user workflows
- Error recovery scenarios
- Performance under load

### Performance Targets

- Message processing: <2s
- Patch application: <500ms
- WebSocket latency: <100ms
- UI responsiveness: 60fps

## Monitoring & Observability

### Metrics

- Message processing time
- Patch acceptance rate
- Agent success/failure rates
- WebSocket connection health

### Logging

- All agent interactions
- Patch application events
- Error conditions with context
- User interaction patterns

### Alerts

- Agent failure rate >5%
- WebSocket disconnections
- Database transaction failures
- High latency warnings

## Security Considerations

### Authentication

- All endpoints require valid user session
- Project access control enforced
- WebSocket connections authenticated

### Data Protection

- Conversation data encrypted at rest
- Artifacts stored securely
- PII handling compliance

### Rate Limiting

- Agent calls limited per user
- WebSocket connections throttled
- File upload size restrictions

## Future Enhancements

### Short-term (Next Quarter)

- Mobile-responsive chat interface
- Keyboard shortcuts and hotkeys
- Drag-and-drop patch reordering
- Custom agent templates

### Medium-term (Next 6 Months)

- Voice input with transcription
- Image analysis and OCR
- Integration with external tools
- Team collaboration features

### Long-term (Next Year)

- Multi-modal AI interactions
- Predictive task suggestions
- Advanced analytics dashboard
- API for third-party integrations

## Success Metrics

### User Experience

- Time from idea to structured project: <5 minutes
- Patch acceptance rate: >80%
- User session duration: >15 minutes
- Feature adoption rate: >60%

### Technical Performance

- System uptime: >99.9%
- Response time: <2s average
- Error rate: <1%
- Test coverage: >90%

### Business Impact

- User engagement increase: >50%
- Project completion rate: >70%
- Feature usage growth: >30% monthly
- User satisfaction: >4.5/5

---

This plan provides a comprehensive roadmap for implementing the chat panel with patch suggestion/acceptance flow. Each phase builds incrementally on the previous one, ensuring we can ship value early while working toward the full vision.
