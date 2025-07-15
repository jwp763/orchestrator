import { describe, it, expect } from 'vitest';
import { parseResponseToChanges, parseRawPatchToChanges } from '../patchParser';
import type { PlannerResponse } from '../../types/api';

describe('patchParser', () => {
  describe('parseResponseToChanges', () => {
    it('should parse project metadata into changes', () => {
      const response: PlannerResponse = {
        success: true,
        project: {
          name: 'Test Project',
          description: 'A test project',
          status: 'planning',
          priority: 'high',
          tags: ['test', 'demo'],
          estimated_total_minutes: 120,
          estimated_total_hours: 2
        },
        tasks: []
      };

      const changes = parseResponseToChanges(response);

      expect(changes).toHaveLength(6);
      expect(changes[0]).toEqual({
        type: 'project',
        field: 'name',
        oldValue: null,
        newValue: 'Test Project',
        display: 'Create project: Test Project'
      });
      expect(changes[1]).toEqual({
        type: 'project',
        field: 'description',
        oldValue: null,
        newValue: 'A test project',
        display: 'Set description: A test project'
      });
      expect(changes[2]).toEqual({
        type: 'project',
        field: 'status',
        oldValue: null,
        newValue: 'planning',
        display: 'Set status: planning'
      });
      expect(changes[3]).toEqual({
        type: 'project',
        field: 'priority',
        oldValue: null,
        newValue: 'high',
        display: 'Set priority: high'
      });
      expect(changes[4]).toEqual({
        type: 'project',
        field: 'tags',
        oldValue: null,
        newValue: ['test', 'demo'],
        display: 'Add tags: test, demo'
      });
      expect(changes[5]).toEqual({
        type: 'project',
        field: 'estimated_total_minutes',
        oldValue: null,
        newValue: 120,
        display: 'Set estimate: 120 minutes (2 hours)'
      });
    });

    it('should parse task metadata into changes', () => {
      const response: PlannerResponse = {
        success: true,
        tasks: [
          {
            title: 'First Task',
            description: 'Task description',
            status: 'todo',
            priority: 'medium',
            estimated_minutes: 60
          },
          {
            title: 'Second Task',
            description: 'Another task',
            status: 'in_progress',
            priority: 'high',
            estimated_minutes: 90
          }
        ]
      };

      const changes = parseResponseToChanges(response);

      expect(changes).toHaveLength(10); // 5 fields × 2 tasks
      
      // First task
      expect(changes[0]).toEqual({
        type: 'task',
        taskId: 'task-1',
        field: 'title',
        oldValue: null,
        newValue: 'First Task',
        display: 'Create task: First Task'
      });
      expect(changes[1]).toEqual({
        type: 'task',
        taskId: 'task-1',
        field: 'description',
        oldValue: null,
        newValue: 'Task description',
        display: 'Set description: Task description'
      });
      expect(changes[4]).toEqual({
        type: 'task',
        taskId: 'task-1',
        field: 'estimated_minutes',
        oldValue: null,
        newValue: 60,
        display: 'Set estimate: 60 minutes (1 hours)'
      });

      // Second task
      expect(changes[5]).toEqual({
        type: 'task',
        taskId: 'task-2',
        field: 'title',
        oldValue: null,
        newValue: 'Second Task',
        display: 'Create task: Second Task'
      });
      expect(changes[9]).toEqual({
        type: 'task',
        taskId: 'task-2',
        field: 'estimated_minutes',
        oldValue: null,
        newValue: 90,
        display: 'Set estimate: 90 minutes (1.5 hours)'
      });
    });

    it('should handle minimal response', () => {
      const response: PlannerResponse = {
        success: true,
        tasks: []
      };

      const changes = parseResponseToChanges(response);

      expect(changes).toHaveLength(0);
    });

    it('should handle project without optional fields', () => {
      const response: PlannerResponse = {
        success: true,
        project: {
          name: 'Simple Project',
          description: '',
          status: 'planning',
          priority: 'medium',
          tags: []
        },
        tasks: []
      };

      const changes = parseResponseToChanges(response);

      expect(changes).toHaveLength(3); // name, status, priority
      expect(changes[0].field).toBe('name');
      expect(changes[1].field).toBe('status');
      expect(changes[2].field).toBe('priority');
    });

    it('should handle task without optional fields', () => {
      const response: PlannerResponse = {
        success: true,
        tasks: [
          {
            title: 'Simple Task',
            description: '',
            status: 'todo',
            priority: 'medium'
          }
        ]
      };

      const changes = parseResponseToChanges(response);

      expect(changes).toHaveLength(3); // title, status, priority
      expect(changes[0].field).toBe('title');
      expect(changes[1].field).toBe('status');
      expect(changes[2].field).toBe('priority');
    });
  });

  describe('parseRawPatchToChanges', () => {
    it('should parse project patches', () => {
      const rawPatch = {
        project_patches: [
          {
            op: 'create',
            name: 'New Project',
            status: 'planning',
            priority: 'high'
          }
        ],
        task_patches: []
      };

      const changes = parseRawPatchToChanges(rawPatch);

      expect(changes).toHaveLength(0); // Skipped because handled by metadata
    });

    it('should parse task patches', () => {
      const rawPatch = {
        project_patches: [],
        task_patches: [
          {
            op: 'update',
            task_id: 'task-123',
            title: 'Updated Task',
            status: 'in_progress'
          }
        ]
      };

      const changes = parseRawPatchToChanges(rawPatch);

      expect(changes).toHaveLength(2); // title and status for update operation
      expect(changes[0].field).toBe('title');
      expect(changes[1].field).toBe('status');
    });

    it('should handle invalid raw patch', () => {
      expect(parseRawPatchToChanges(null)).toEqual([]);
      expect(parseRawPatchToChanges(undefined)).toEqual([]);
      expect(parseRawPatchToChanges('invalid')).toEqual([]);
      expect(parseRawPatchToChanges({})).toEqual([]);
    });

    it('should handle empty patches', () => {
      const rawPatch = {
        project_patches: [],
        task_patches: []
      };

      const changes = parseRawPatchToChanges(rawPatch);

      expect(changes).toHaveLength(0);
    });
  });

  describe('integration with full response', () => {
    it('should parse complete response with both metadata and raw patches', () => {
      const response: PlannerResponse = {
        success: true,
        project: {
          name: 'Full Project',
          description: 'Complete project',
          status: 'planning',
          priority: 'high',
          tags: ['full', 'complete'],
          estimated_total_minutes: 240
        },
        tasks: [
          {
            title: 'Main Task',
            description: 'Primary task',
            status: 'todo',
            priority: 'high',
            estimated_minutes: 120
          }
        ],
        raw_patch: {
          project_patches: [
            {
              op: 'create',
              name: 'Full Project',
              status: 'planning'
            }
          ],
          task_patches: [
            {
              op: 'create',
              title: 'Main Task',
              status: 'todo'
            }
          ]
        }
      };

      const changes = parseResponseToChanges(response);

      // Should have changes from metadata (project: 6, task: 5)
      expect(changes.length).toBeGreaterThan(0);
      expect(changes.some(c => c.field === 'name' && c.newValue === 'Full Project')).toBe(true);
      expect(changes.some(c => c.field === 'title' && c.newValue === 'Main Task')).toBe(true);
    });

    it('should handle response with only raw patches', () => {
      const response: PlannerResponse = {
        success: true,
        tasks: [],
        raw_patch: {
          project_patches: [
            {
              op: 'update',
              project_id: 'proj-123',
              name: 'Updated Project',
              priority: 'critical'
            }
          ],
          task_patches: []
        }
      };

      const changes = parseResponseToChanges(response);

      // Should have changes from raw patch processing
      expect(changes.length).toBeGreaterThan(0);
    });
  });
});