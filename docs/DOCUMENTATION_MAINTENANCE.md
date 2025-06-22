# Documentation Maintenance Guidelines

## Overview

This document establishes clear rules and processes for maintaining the project documentation to ensure it remains accurate, coherent, and useful throughout the project lifecycle.

## Core Principles

### 1. Planning Mode Only Rule
**CRITICAL**: Documentation changes should ONLY be suggested during planning mode conversations, and ONLY implemented after explicit user approval.

- ✅ **Allowed**: Suggesting documentation updates during planning discussions
- ✅ **Allowed**: Making approved changes after user explicitly approves
- ❌ **Forbidden**: Making documentation changes during regular development work
- ❌ **Forbidden**: Making changes without explicit user approval

### 2. Coherence Requirement
All documentation must remain internally consistent and coherent across documents.

- Plans must align with the overall vision and architecture
- Timeline estimates should be realistic and account for dependencies
- Success metrics should be measurable and achievable
- Changes in one document may require updates to related documents

### 3. Human-Readable Language
Documentation should be written for human comprehension and modification.

- Use clear, concise language without excessive technical jargon
- Organize information hierarchically with clear headings and structure
- Include concrete examples and implementation details where helpful
- Maintain consistent terminology across all documents

## Document Structure and Relationships

### Primary Documents
1. **README.md** - Project overview and quick start guide
2. **PROGRESS.md** - Detailed status of completed work
3. **SHORT_TERM_PLAN.md** - Next 2-4 weeks of detailed work plans
4. **MID_TERM_PLAN.md** - 2-6 month roadmap with moderate detail
5. **LONG_TERM_VISION.md** - 6+ month vision with broad concepts
6. **DOCUMENTATION_MAINTENANCE.md** - This file with maintenance rules

### Document Dependencies
```
LONG_TERM_VISION.md
       ↓
MID_TERM_PLAN.md
       ↓
SHORT_TERM_PLAN.md
       ↓
PROGRESS.md
       ↓
README.md
```

Changes flow down the hierarchy - vision changes may impact all downstream documents.

## Maintenance Procedures

### Regular Updates (User-Initiated)

#### When to Update Documents

1. **PROGRESS.md**
   - Update weekly or after completing major milestones
   - Add new completed features and mark tasks as done
   - Update status tables and completion percentages
   - Document any architectural decisions or changes

2. **SHORT_TERM_PLAN.md**
   - Review and update every 1-2 weeks
   - Adjust timelines based on actual progress
   - Add new tasks that emerge during development
   - Reorder priorities based on changing requirements

3. **MID_TERM_PLAN.md**
   - Review monthly or after completing short-term phases
   - Adjust plans based on lessons learned
   - Update feature specifications based on user feedback
   - Revise success metrics based on actual capabilities

4. **LONG_TERM_VISION.md**
   - Review quarterly or when major strategic changes occur
   - Update based on technology developments
   - Adjust based on market research and user needs
   - Refine based on feasibility learnings

#### How to Request Updates

1. **Planning Mode Initiation**: Start a planning conversation explicitly
2. **Document Review**: Specify which documents need updating
3. **Change Description**: Clearly describe what changes are needed and why
4. **Approval Process**: Review suggested changes before implementation
5. **Coherence Check**: Ensure changes maintain consistency across documents

### Change Management Process

#### Step 1: Assessment Phase
- Identify which documents are affected by proposed changes
- Assess impact on timelines, dependencies, and success metrics
- Consider implications for both technical and strategic aspects
- Evaluate resource requirements for implementing changes

#### Step 2: Planning Phase
- Draft specific changes to each affected document
- Ensure consistency across all related documents
- Verify that changes align with overall project vision
- Confirm feasibility of updated timelines and goals

#### Step 3: Review Phase
- Present complete set of proposed changes
- Highlight any significant shifts in direction or priorities
- Identify any risks or concerns with the updated plans
- Request explicit approval before implementing any changes

#### Step 4: Implementation Phase
- Make approved changes across all affected documents
- Update cross-references and internal links
- Verify consistency of terminology and formatting
- Commit changes with clear descriptions of what was updated

### Quality Assurance

#### Consistency Checks
- **Terminology**: Use consistent terms across all documents
- **Timelines**: Ensure dates and durations align between documents
- **Dependencies**: Verify task dependencies are properly reflected
- **Success Metrics**: Confirm metrics are achievable and measurable

#### Content Quality
- **Clarity**: Ensure all instructions and descriptions are clear
- **Completeness**: Verify all necessary information is included
- **Accuracy**: Confirm all technical details are correct
- **Relevance**: Remove outdated or no-longer-relevant information

#### Structural Integrity
- **Hierarchy**: Maintain clear document hierarchy and flow
- **Cross-References**: Update links and references when moving content
- **Formatting**: Maintain consistent markdown formatting
- **Organization**: Keep related information grouped logically

## Specific Document Guidelines

### PROGRESS.md Maintenance
- **Weekly Updates**: Add completed work and update status tables
- **Milestone Tracking**: Mark major milestones as achieved
- **Architecture Changes**: Document any significant technical decisions
- **Lessons Learned**: Include insights that inform future planning

### SHORT_TERM_PLAN.md Maintenance
- **Task Granularity**: Keep tasks at 1-4 day granularity for actionability
- **Clear Instructions**: Provide enough detail for independent implementation
- **Success Criteria**: Define clear completion criteria for each task
- **Risk Mitigation**: Update risk assessments based on new learnings

### MID_TERM_PLAN.md Maintenance
- **Feature Evolution**: Update feature descriptions based on user feedback
- **Technology Updates**: Incorporate new technologies or approaches
- **Resource Planning**: Adjust resource estimates based on actual consumption
- **Market Alignment**: Update based on market research and competitive analysis

### LONG_TERM_VISION.md Maintenance
- **Strategic Alignment**: Ensure vision aligns with user goals and market needs
- **Technology Roadmap**: Update based on technology advancement predictions
- **Feasibility Assessment**: Adjust based on learnings about what's achievable
- **Impact Planning**: Refine expected outcomes and success metrics

## Emergency Procedures

### Urgent Changes Required
If urgent documentation updates are needed outside of planning mode:

1. **Immediate Notification**: Clearly state this is an emergency documentation update
2. **Justification**: Explain why the change cannot wait for planning mode
3. **Minimal Scope**: Limit changes to only what's absolutely necessary
4. **Follow-Up**: Schedule a proper planning review to address broader implications

### Recovery from Inconsistencies
If documentation becomes inconsistent or incoherent:

1. **Halt Development**: Stop making further changes until documentation is fixed
2. **Assessment**: Review all documents to identify inconsistencies
3. **Planning Session**: Dedicated planning session to resolve all issues
4. **Comprehensive Update**: Update all affected documents to restore coherence

## Tools and Automation

### Recommended Tools
- **Version Control**: Use git to track all documentation changes
- **Link Checking**: Regularly verify internal and external links
- **Spell Check**: Use automated spell checking for all documents
- **Consistency Checking**: Develop tools to check terminology consistency

### Automation Opportunities
- **Status Updates**: Automatically update progress indicators where possible
- **Cross-Reference Validation**: Tools to verify internal document references
- **Timeline Tracking**: Automated tracking of planned vs actual timelines
- **Metric Collection**: Automated collection of success metrics where possible

## Success Metrics for Documentation

### Quality Metrics
- **Consistency Score**: Percentage of terminology usage that's consistent
- **Completeness Score**: Percentage of planned features with adequate documentation
- **Accuracy Score**: Percentage of documented features that work as described
- **Usefulness Score**: User feedback on documentation helpfulness

### Process Metrics
- **Update Frequency**: How often documents are updated relative to development pace
- **Review Efficiency**: Time from planning discussion to documentation update
- **Error Rate**: Frequency of documentation errors or inconsistencies
- **User Satisfaction**: Developer satisfaction with documentation quality and currency

### Maintenance Health
- **Staleness Indicators**: How quickly outdated information is identified and updated
- **Coverage Completeness**: Percentage of features with current documentation
- **Planning Effectiveness**: How well documentation planning translates to successful implementation
- **Strategic Alignment**: How well detailed plans align with long-term vision

## Violations and Enforcement

### Common Violations
- Making documentation changes during development without planning approval
- Creating inconsistencies between related documents
- Using unclear language or excessive jargon
- Failing to update dependent documents when making changes

### Enforcement Process
1. **Detection**: Identify violations through regular review or automated checking
2. **Assessment**: Evaluate impact of violation on documentation coherence
3. **Correction**: Plan and implement corrections to restore documentation quality
4. **Prevention**: Update processes to prevent similar violations in the future

Remember: The goal is to maintain living documentation that accurately reflects the project state and provides clear guidance for future development while respecting the collaborative nature of human-AI planning sessions.