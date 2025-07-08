import { renderHook, act } from '@testing-library/react'
import { usePlannerAPI } from './usePlannerAPI'
import type { PlannerRequest, PlannerResponse, ProvidersResponse, ConfigResponse, ErrorResponse } from '../types/api'

// Mock fetch
const mockFetch = vi.fn()
global.fetch = mockFetch

describe('usePlannerAPI', () => {
  beforeEach(() => {
    mockFetch.mockClear()
  })

  describe('initial state', () => {
    test('should have correct initial state', () => {
      const { result } = renderHook(() => usePlannerAPI())

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe(null)
      expect(typeof result.current.generatePlan).toBe('function')
      expect(typeof result.current.getProviders).toBe('function')
      expect(typeof result.current.getConfig).toBe('function')
      expect(typeof result.current.clearError).toBe('function')
    })
  })

  describe('generatePlan', () => {
    test('should successfully generate a plan', async () => {
      const mockRequest: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
      }

      const mockResponse: PlannerResponse = {
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

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => usePlannerAPI())

      let planResult: PlannerResponse | null = null
      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest)
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe(null)
      expect(planResult).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/generate',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(mockRequest),
        }
      )
    })

    test('should handle API errors', async () => {
      const mockRequest: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
      }

      const mockErrorResponse: ErrorResponse = {
        error: 'Invalid request',
        details: 'Missing required field',
        code: 'VALIDATION_ERROR',
      }

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => mockErrorResponse,
      })

      const { result } = renderHook(() => usePlannerAPI())

      let planResult: PlannerResponse | null = null
      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest)
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe('Invalid request')
      expect(planResult).toBe(null)
    })

    test('should handle network errors', async () => {
      const mockRequest: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
      }

      mockFetch.mockRejectedValueOnce(new Error('Network error'))

      const { result } = renderHook(() => usePlannerAPI())

      let planResult: PlannerResponse | null = null
      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest)
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe('Network error')
      expect(planResult).toBe(null)
    })

    test('should set loading state during request', async () => {
      const mockRequest: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
      }

      let resolvePromise: (value: any) => void
      const mockPromise = new Promise((resolve) => {
        resolvePromise = resolve
      })

      mockFetch.mockReturnValueOnce(mockPromise)

      const { result } = renderHook(() => usePlannerAPI())

      act(() => {
        result.current.generatePlan(mockRequest)
      })

      expect(result.current.loading).toBe(true)
      expect(result.current.error).toBe(null)

      await act(async () => {
        resolvePromise!({
          ok: true,
          json: async () => ({ success: true, project: {}, tasks: [] }),
        })
      })

      expect(result.current.loading).toBe(false)
    })
  })

  describe('getProviders', () => {
    test('should successfully get providers', async () => {
      const mockResponse: ProvidersResponse = {
        providers: [
          {
            name: 'openai',
            display_name: 'OpenAI',
            models: [
              {
                name: 'gpt-4',
                description: 'GPT-4 model',
                max_tokens: 8192,
                supports_tools: true,
              },
            ],
            default_model: 'gpt-4',
          },
        ],
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => usePlannerAPI())

      let providersResult: ProvidersResponse | null = null
      await act(async () => {
        providersResult = await result.current.getProviders()
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe(null)
      expect(providersResult).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/providers',
        {
          headers: { 'Content-Type': 'application/json' },
        }
      )
    })
  })

  describe('getConfig', () => {
    test('should successfully get config', async () => {
      const mockResponse: ConfigResponse = {
        default_config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
        providers: [],
      }

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      })

      const { result } = renderHook(() => usePlannerAPI())

      let configResult: ConfigResponse | null = null
      await act(async () => {
        configResult = await result.current.getConfig()
      })

      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe(null)
      expect(configResult).toEqual(mockResponse)
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/config',
        {
          headers: { 'Content-Type': 'application/json' },
        }
      )
    })
  })

  describe('clearError', () => {
    test('should clear error state', async () => {
      const mockRequest: PlannerRequest = {
        project_idea: 'Build a todo app',
        config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
      }

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Test error' }),
      })

      const { result } = renderHook(() => usePlannerAPI())

      // Generate an error
      await act(async () => {
        await result.current.generatePlan(mockRequest)
      })

      expect(result.current.error).toBe('Test error')

      // Clear the error
      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBe(null)
    })
  })

  describe('error handling', () => {
    test('should handle JSON parsing errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Invalid JSON')
        },
      })

      const { result } = renderHook(() => usePlannerAPI())

      await act(async () => {
        await result.current.getProviders()
      })

      expect(result.current.error).toBe('Invalid JSON')
    })

    test('should handle non-Error objects', async () => {
      mockFetch.mockRejectedValueOnce('String error')

      const { result } = renderHook(() => usePlannerAPI())

      await act(async () => {
        await result.current.getProviders()
      })

      expect(result.current.error).toBe('An unknown error occurred')
    })

    test('should handle HTTP errors without error response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({}),
      })

      const { result } = renderHook(() => usePlannerAPI())

      await act(async () => {
        await result.current.getProviders()
      })

      expect(result.current.error).toBe('HTTP error! status: 404')
    })
  })

  describe('concurrent requests', () => {
    test('should handle multiple concurrent requests', async () => {
      const mockResponse1: ProvidersResponse = { providers: [] }
      const mockResponse2: ConfigResponse = {
        default_config: {
          provider: 'openai',
          model: 'gpt-4',
          max_retries: 2,
          create_milestones: true,
          max_milestones: 5,
        },
        providers: [],
      }

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse1,
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse2,
        })

      const { result } = renderHook(() => usePlannerAPI())

      let providersResult: ProvidersResponse | null = null
      let configResult: ConfigResponse | null = null

      await act(async () => {
        const [providers, config] = await Promise.all([
          result.current.getProviders(),
          result.current.getConfig(),
        ])
        providersResult = providers
        configResult = config
      })

      expect(providersResult).toEqual(mockResponse1)
      expect(configResult).toEqual(mockResponse2)
      expect(result.current.loading).toBe(false)
      expect(result.current.error).toBe(null)
    })
  })
})