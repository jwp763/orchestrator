import type {
  PlannerConfig,
  PlannerRequest,
  ProjectData,
  TaskData,
  PlannerResponse,
  ProviderModel,
  Provider,
  ProvidersResponse,
  ConfigResponse,
  ErrorResponse,
  UserPreferences,
  ProjectHistory,
} from './api'

describe('API Types', () => {
  describe('PlannerConfig', () => {
    test('should match expected structure', () => {
      const config: PlannerConfig = {
        provider: 'openai',
        model: 'gpt-4',
        max_retries: 2,
        create_milestones: true,
        max_milestones: 5,
        temperature: 0.7,
        max_tokens: 2000,
      }

      expect(config.provider).toBe('openai')
      expect(config.model).toBe('gpt-4')
      expect(config.max_retries).toBe(2)
      expect(config.create_milestones).toBe(true)
      expect(config.max_milestones).toBe(5)
      expect(config.temperature).toBe(0.7)
      expect(config.max_tokens).toBe(2000)
    })

    test('should support all provider types', () => {
      const providers: PlannerConfig['provider'][] = ['openai', 'anthropic', 'gemini', 'xai']
      
      providers.forEach(provider => {
        const config: PlannerConfig = {
          provider,
          model: 'test-model',
          max_retries: 1,
          create_milestones: false,
          max_milestones: 3,
        }
        expect(config.provider).toBe(provider)
      })
    })
  })

  describe('PlannerRequest', () => {
    test('should match expected structure', () => {
      const request: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'anthropic',
          model: 'claude-3-sonnet',
          max_retries: 3,
          create_milestones: true,
          max_milestones: 8,
        },
      }

      expect(request.project_idea).toBe('Build a todo app')
      expect(request.config.provider).toBe('anthropic')
      expect(request.config.model).toBe('claude-3-sonnet')
    })
  })

  describe('ProjectData', () => {
    test('should match expected structure', () => {
      const project: ProjectData = {
        id: 'proj-123',
        title: 'Todo App',
        description: 'A simple todo application',
        status: 'active',
        priority: 'high',
        estimated_hours: 40,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      }

      expect(project.id).toBe('proj-123')
      expect(project.title).toBe('Todo App')
      expect(project.status).toBe('active')
      expect(project.priority).toBe('high')
      expect(project.estimated_hours).toBe(40)
    })

    test('should support all status types', () => {
      const statuses: ProjectData['status'][] = ['active', 'completed', 'on_hold']
      
      statuses.forEach(status => {
        const project: ProjectData = {
          id: 'test',
          title: 'Test',
          description: 'Test',
          status,
          priority: 'medium',
          estimated_hours: 10,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        }
        expect(project.status).toBe(status)
      })
    })

    test('should support all priority types', () => {
      const priorities: ProjectData['priority'][] = ['low', 'medium', 'high']
      
      priorities.forEach(priority => {
        const project: ProjectData = {
          id: 'test',
          title: 'Test',
          description: 'Test',
          status: 'active',
          priority,
          estimated_hours: 10,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        }
        expect(project.priority).toBe(priority)
      })
    })
  })

  describe('TaskData', () => {
    test('should match expected structure', () => {
      const task: TaskData = {
        id: 'task-123',
        project_id: 'proj-123',
        title: 'Create user interface',
        description: 'Design and implement the UI',
        status: 'pending',
        priority: 'high',
        estimated_hours: 8,
        parent_task_id: 'task-parent',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      }

      expect(task.id).toBe('task-123')
      expect(task.project_id).toBe('proj-123')
      expect(task.title).toBe('Create user interface')
      expect(task.status).toBe('pending')
      expect(task.priority).toBe('high')
      expect(task.estimated_hours).toBe(8)
      expect(task.parent_task_id).toBe('task-parent')
    })

    test('should support all task status types', () => {
      const statuses: TaskData['status'][] = ['pending', 'in_progress', 'completed']
      
      statuses.forEach(status => {
        const task: TaskData = {
          id: 'test',
          project_id: 'proj-test',
          title: 'Test',
          description: 'Test',
          status,
          priority: 'medium',
          estimated_hours: 5,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        }
        expect(task.status).toBe(status)
      })
    })

    test('should have optional parent_task_id', () => {
      const task: TaskData = {
        id: 'task-123',
        project_id: 'proj-123',
        title: 'Root task',
        description: 'A root level task',
        status: 'pending',
        priority: 'medium',
        estimated_hours: 5,
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      }

      expect(task.parent_task_id).toBeUndefined()
    })
  })

  describe('PlannerResponse', () => {
    test('should match expected structure for success', () => {
      const response: PlannerResponse = {
        success: true,
        project: {
          id: 'proj-123',
          title: 'Todo App',
          description: 'A simple todo application',
          status: 'active',
          priority: 'high',
          estimated_hours: 40,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        tasks: [
          {
            id: 'task-123',
            project_id: 'proj-123',
            title: 'Create UI',
            description: 'Design interface',
            status: 'pending',
            priority: 'high',
            estimated_hours: 8,
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
          },
        ],
        message: 'Project created successfully',
      }

      expect(response.success).toBe(true)
      expect(response.project.id).toBe('proj-123')
      expect(response.tasks).toHaveLength(1)
      expect(response.tasks[0].id).toBe('task-123')
      expect(response.message).toBe('Project created successfully')
    })

    test('should have optional message field', () => {
      const response: PlannerResponse = {
        success: true,
        project: {
          id: 'proj-123',
          title: 'Todo App',
          description: 'A simple todo application',
          status: 'active',
          priority: 'high',
          estimated_hours: 40,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        tasks: [],
      }

      expect(response.message).toBeUndefined()
    })
  })

  describe('Provider and ProviderModel', () => {
    test('should match expected structure', () => {
      const model: ProviderModel = {
        name: 'gpt-4',
        description: 'GPT-4 model',
        max_tokens: 8192,
        supports_tools: true,
      }

      const provider: Provider = {
        name: 'openai',
        display_name: 'OpenAI',
        models: [model],
        default_model: 'gpt-4',
      }

      expect(model.name).toBe('gpt-4')
      expect(model.supports_tools).toBe(true)
      expect(provider.name).toBe('openai')
      expect(provider.display_name).toBe('OpenAI')
      expect(provider.models).toHaveLength(1)
      expect(provider.default_model).toBe('gpt-4')
    })
  })

  describe('UserPreferences', () => {
    test('should match expected structure', () => {
      const preferences: UserPreferences = {
        lastConfig: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
        theme: 'dark',
        autoSave: true,
      }

      expect(preferences.lastConfig.provider).toBe('openai')
      expect(preferences.theme).toBe('dark')
      expect(preferences.autoSave).toBe(true)
    })

    test('should support both theme types', () => {
      const themes: UserPreferences['theme'][] = ['light', 'dark']
      
      themes.forEach(theme => {
        const preferences: UserPreferences = {
          lastConfig: {
            provider: 'openai',
            model: 'gpt-4',
            max_retries: 2,
            create_milestones: true,
            max_milestones: 5,
          },
          theme,
          autoSave: false,
        }
        expect(preferences.theme).toBe(theme)
      })
    })
  })

  describe('ErrorResponse', () => {
    test('should match expected structure', () => {
      const error: ErrorResponse = {
        error: 'Invalid request',
        details: 'Missing required field: project_idea',
        code: 'VALIDATION_ERROR',
      }

      expect(error.error).toBe('Invalid request')
      expect(error.details).toBe('Missing required field: project_idea')
      expect(error.code).toBe('VALIDATION_ERROR')
    })

    test('should have optional details and code fields', () => {
      const error: ErrorResponse = {
        error: 'Internal server error',
      }

      expect(error.error).toBe('Internal server error')
      expect(error.details).toBeUndefined()
      expect(error.code).toBeUndefined()
    })
  })
})