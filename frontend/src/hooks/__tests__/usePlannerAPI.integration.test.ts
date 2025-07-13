/**
 * Integration tests for usePlannerAPI hook with real API calls
 * 
 * Tests the hook's interaction with the planner API endpoints,
 * including error handling, loading states, and response parsing
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { usePlannerAPI } from '../usePlannerAPI';
import type {
  PlannerRequest,
  PlannerResponse,
  ProvidersResponse,
  ConfigResponse,
} from '../../types/api';

// Mock fetch globally
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('usePlannerAPI Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('generatePlan', () => {
    it('should generate plan successfully', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Create a web application',
        config: {
          provider: 'anthropic',
          model: 'claude-3-sonnet-20240229',
          temperature: 0.7,
          max_tokens: 4000,
          include_milestones: true,
          max_milestones: 5,
          max_retries: 3,
          retry_delay: 1000
        }
      };

      const mockResponse: PlannerResponse = {
        success: true,
        plan: {
          project: {
            name: 'Web Application Project',
            description: 'A comprehensive web application',
            status: 'planning',
            priority: 'high',
            tags: ['web', 'development']
          },
          tasks: [
            {
              title: 'Setup Development Environment',
              description: 'Configure development tools and environment',
              priority: 'high',
              estimated_minutes: 120
            },
            {
              title: 'Design Database Schema',
              description: 'Create database design and relationships',
              priority: 'medium',
              estimated_minutes: 180
            }
          ]
        },
        usage: {
          prompt_tokens: 150,
          completion_tokens: 800,
          total_tokens: 950
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => usePlannerAPI());

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      let planResult: PlannerResponse | null = null;

      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest);
      });

      expect(planResult).toEqual(mockResponse);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/generate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(mockRequest),
        }
      );
    });

    it('should handle API error response', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Invalid request',
        config: {
          provider: 'anthropic',
          model: 'claude-3-sonnet-20240229'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({
          error: 'Invalid request: idea cannot be empty'
        }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let planResult: PlannerResponse | null = null;

      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest);
      });

      expect(planResult).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Invalid request: idea cannot be empty');
    });

    it('should handle network error', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
      };

      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => usePlannerAPI());

      let planResult: PlannerResponse | null = null;

      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest);
      });

      expect(planResult).toBeNull();
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Network error');
    });

    it('should handle JSON parsing error', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.reject(new Error('Invalid JSON')),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let planResult: PlannerResponse | null = null;

      await act(async () => {
        planResult = await result.current.generatePlan(mockRequest);
      });

      expect(planResult).toBeNull();
      expect(result.current.error).toBe('Invalid JSON');
    });

    it('should handle HTTP error without error response', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
      };

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.reject(new Error('Not JSON')),
      });

      const { result } = renderHook(() => usePlannerAPI());

      await act(async () => {
        await result.current.generatePlan(mockRequest);
      });

      expect(result.current.error).toBe('Not JSON');
    });

    it('should handle non-Error objects', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
      };

      mockFetch.mockRejectedValueOnce('String error');

      const { result } = renderHook(() => usePlannerAPI());

      await act(async () => {
        await result.current.generatePlan(mockRequest);
      });

      expect(result.current.error).toBe('An unknown error occurred');
    });
  });

  describe('getProviders', () => {
    it('should get providers successfully', async () => {
      const mockResponse: ProvidersResponse = {
        providers: [
          {
            id: 'anthropic',
            name: 'Anthropic',
            models: [
              {
                id: 'claude-3-sonnet-20240229',
                name: 'Claude 3 Sonnet',
                max_tokens: 4000,
                supports_streaming: true
              },
              {
                id: 'claude-3-haiku-20240307',
                name: 'Claude 3 Haiku',
                max_tokens: 4000,
                supports_streaming: true
              }
            ],
            available: true
          },
          {
            id: 'openai',
            name: 'OpenAI',
            models: [
              {
                id: 'gpt-4',
                name: 'GPT-4',
                max_tokens: 8000,
                supports_streaming: true
              }
            ],
            available: false
          }
        ]
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let providersResult: ProvidersResponse | null = null;

      await act(async () => {
        providersResult = await result.current.getProviders();
      });

      expect(providersResult).toEqual(mockResponse);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/providers',
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    });

    it('should handle providers API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: () => Promise.resolve({
          error: 'Internal server error'
        }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let providersResult: ProvidersResponse | null = null;

      await act(async () => {
        providersResult = await result.current.getProviders();
      });

      expect(providersResult).toBeNull();
      expect(result.current.error).toBe('Internal server error');
    });
  });

  describe('getConfig', () => {
    it('should get config successfully', async () => {
      const mockResponse: ConfigResponse = {
        default_provider: 'anthropic',
        default_model: 'claude-3-sonnet-20240229',
        default_temperature: 0.7,
        default_max_tokens: 4000,
        default_include_milestones: true,
        default_max_milestones: 5,
        default_max_retries: 3,
        default_retry_delay: 1000,
        available_providers: ['anthropic', 'openai'],
        rate_limits: {
          requests_per_minute: 60,
          tokens_per_minute: 100000
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let configResult: ConfigResponse | null = null;

      await act(async () => {
        configResult = await result.current.getConfig();
      });

      expect(configResult).toEqual(mockResponse);
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/config',
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    });

    it('should handle config API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: () => Promise.resolve({
          error: 'Unauthorized access'
        }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      let configResult: ConfigResponse | null = null;

      await act(async () => {
        configResult = await result.current.getConfig();
      });

      expect(configResult).toBeNull();
      expect(result.current.error).toBe('Unauthorized access');
    });
  });

  describe('loading states', () => {
    it('should manage loading state correctly during generatePlan', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
      };

      // Mock a delayed response
      mockFetch.mockImplementationOnce(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({
              success: true,
              plan: { project: {}, tasks: [] }
            }),
          }), 100)
        )
      );

      const { result } = renderHook(() => usePlannerAPI());

      expect(result.current.loading).toBe(false);

      act(() => {
        result.current.generatePlan(mockRequest);
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });

    it('should manage loading state correctly during getProviders', async () => {
      // Mock a delayed response
      mockFetch.mockImplementationOnce(() =>
        new Promise(resolve =>
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({ providers: [] }),
          }), 50)
        )
      );

      const { result } = renderHook(() => usePlannerAPI());

      expect(result.current.loading).toBe(false);

      act(() => {
        result.current.getProviders();
      });

      expect(result.current.loading).toBe(true);

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });
    });
  });

  describe('error management', () => {
    it('should clear error state', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ error: 'Test error' }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      // Trigger an error
      await act(async () => {
        await result.current.generatePlan({
          idea: 'Test',
          config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
        });
      });

      expect(result.current.error).toBe('Test error');

      // Clear the error
      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });

    it('should clear error state when making new request', async () => {
      // First request fails
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: () => Promise.resolve({ error: 'First error' }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      await act(async () => {
        await result.current.generatePlan({
          idea: 'Test',
          config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
        });
      });

      expect(result.current.error).toBe('First error');

      // Second request succeeds
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          plan: { project: {}, tasks: [] }
        }),
      });

      await act(async () => {
        await result.current.generatePlan({
          idea: 'Test 2',
          config: { provider: 'anthropic', model: 'claude-3-sonnet-20240229' }
        });
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('request headers and body', () => {
    it('should send correct headers and body for POST request', async () => {
      const mockRequest: PlannerRequest = {
        idea: 'Test idea',
        config: {
          provider: 'anthropic',
          model: 'claude-3-sonnet-20240229',
          temperature: 0.8,
          max_tokens: 2000
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          plan: { project: {}, tasks: [] }
        }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      await act(async () => {
        await result.current.generatePlan(mockRequest);
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/generate',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(mockRequest),
        }
      );
    });

    it('should send correct headers for GET request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ providers: [] }),
      });

      const { result } = renderHook(() => usePlannerAPI());

      await act(async () => {
        await result.current.getProviders();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/planner/providers',
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
    });
  });
});