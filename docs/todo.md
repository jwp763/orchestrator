# TODO - Hierarchical Task-Planner MVP

## Current Sprint (Week 27)

### Phase 0: Foundation Hardening ⏳
- [ ] Task 0.1: Extend Task Model with Hierarchical Fields (1 day)
  - [x] Add hierarchical fields to Task model (90 min)
  - [x] ~~Create Delta table migration (60 min)~~ *Skipped - no existing data*
  - [ ] Extend DeltaManager CRUD operations (75 min)
  - [ ] Update configuration for defaults (45 min)
- [ ] Task 0.2: Create Task Relationship Table (0.5 days)
  - [ ] Design task_links schema (45 min)
  - [ ] Implement graph operations (90 min)

## Upcoming Phases

### Phase 1: Natural Language Planner Engine (Week 28-29) 🤖
- [ ] Task 1.1: Design Planning Prompt System (1.5 days)
  - [ ] Gather real-world examples (90 min)
  - [ ] Develop core planning prompt (120 min)
  - [ ] Implement prompt variations (90 min)
  - [ ] Build evaluation framework (90 min)
- [ ] Task 1.2: Implement Planning Pipeline (2 days)
  - [ ] Create PlannerAgent class (120 min)
  - [ ] Add response parsing & validation (90 min)
  - [ ] Implement plan persistence (120 min)
  - [ ] Add planning analytics (60 min)
- [ ] Task 1.3: Initial Dogfooding - Ingest MVP Plan (0.5 days)
  - [ ] Parse and persist mvp_plan.md

### Phase 2: Task Graph & Splitting API (Week 30) 🌳
- [ ] Task 2.1: Build Recursive Task Operations (1.5 days)
  - [ ] Implement split task API (90 min)
  - [ ] Create smart splitting heuristics (90 min)
  - [ ] Implement merge task API (60 min)
  - [ ] Add batch operations (60 min)
- [ ] Task 2.2: Implement Dependency Management (1 day)
  - [ ] Create dependency parser (90 min)
  - [ ] Build scheduling algorithm (120 min)

### Phase 3: Motion Sync 2.0 (Week 30) 🔄
- [ ] Task 3.1: Enhance Motion Integration for Hierarchies (1.5 days)
  - [ ] Extend Motion client for subtasks (90 min)
  - [ ] Implement duration mapping (60 min)
  - [ ] Build bidirectional status sync (90 min)
  - [ ] Add sync monitoring (60 min)
- [ ] Task 3.2: Activate Motion Sync for MVP Plan (0.5 days)
  - [ ] Run initial MVP project sync to Motion
  - [ ] Transition to Motion-driven project management
- [ ] Task 3.3: Abstract Provider Interface (0.5 days)
  - [ ] Define provider interface (60 min)
  - [ ] Create provider registry (60 min)

### Phase 4: User Experience (Week 31) 🎨
- [ ] Task 4.1: Create Planning Notebook Interface (1 day)
  - [ ] Design input widget (90 min)
  - [ ] Build plan preview (90 min)
- [ ] Task 4.2: Create Visualization Dashboard (1.5 days)
  - [ ] Implement tree visualization (120 min)
  - [ ] Create Gantt chart (90 min)
  - [ ] Add analytics dashboard (90 min)

### Phase 5: Quality & Performance (Week 32) 🚀
- [ ] Task 5.1: Build Quality Assurance System (1.5 days)
  - [ ] Create test data generator (90 min)
  - [ ] Implement planning accuracy tests (90 min)
  - [ ] Add integration tests (90 min)
- [ ] Task 5.2: Performance Optimization (1.5 days)
  - [ ] Load test planning operations (120 min)
  - [ ] Optimize Delta operations (90 min)
  - [ ] Implement caching layer (90 min)

### Phase 6: Documentation & Launch (Week 33) 📚
- [ ] Task 6.1: Create Comprehensive Documentation (1.5 days)
  - [ ] Write user guide (120 min)
  - [ ] Create API documentation (90 min)
  - [ ] Record demo videos (90 min)
- [ ] Task 6.2: Launch Preparation (0.5 days)
  - [ ] Create release notes (60 min)
  - [ ] Publish announcement (60 min)

## Completed ✅

### Documentation
- [x] Create comprehensive MVP plan document
- [x] Update architecture documentation with hierarchical model
- [x] Create data model documentation with migration strategy
- [x] Define clear task/subtask specifications with acceptance criteria

### Phase 0: Foundation Hardening
- [x] Subtask 0.1.1: Add hierarchical fields to Task model (90 min)
  - Added parent_id, estimated_minutes, actual_minutes, depth, dependencies
  - Added validation for positive minutes, depth limits, circular dependencies
  - Created comprehensive tests - all passing ✅

## Key Milestones 🎯

| Week | Milestone |
|------|-----------|
| W27 | Foundation complete, ready for planner development |
| W28-29 | First natural language plan successfully created |
| W30 | MVP plan synced to Motion, team using it |
| W31 | Interactive planning UI available |
| W32 | System handles 10k tasks with <2s response |
| W33 | Public v1.0 release |

## Success Metrics 📊

- **Adoption**: 10+ projects planned in first week
- **Accuracy**: <20% time estimate error
- **Performance**: <2s planning time for typical projects
- **Reliability**: 99.9% uptime for sync operations

## Notes 📝

- This TODO list represents the MVP plan itself - we're dogfooding!
- Each task has detailed specifications in `docs/mvp_plan.md`
- All tasks should be created in the system once Phase 1 is complete
- Regular sync meetings scheduled to review progress

## Quick Links 🔗

- [MVP Plan Details](./mvp_plan.md)
- [Architecture](./architecture.md)
- [Data Model](./data_model.md)
- [Progress Tracking](./PROGRESS.md)