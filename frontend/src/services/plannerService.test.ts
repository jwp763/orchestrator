import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PlannerService, getPlannerService } from './plannerService';
import { ApiClient } from './api';
import type { PlannerRequest, PlannerResponse, ProvidersResponse } from '../types/api';

// Mock the ApiClient
vi.mock('./api', () => ({
  ApiClient: vi.fn().mockImplementation(() => ({
    get: vi.fn(),
    post: vi.fn(),
  })),
}));

describe('PlannerService', () => {
  let service: PlannerService;
  let mockApiClient: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockApiClient = new ApiClient();
    service = new PlannerService(mockApiClient);
  });

  describe('generatePlan', () => {
    it('should call the correct endpoint with request data', async () => {
      const request: PlannerRequest = {
        idea: 'Create a fitness tracking app',
        config: {
          provider: 'openai',
          create_milestones: true,
          max_milestones: 5,
          max_retries: 2,
        },
        context: {},
      };

      const mockResponse: PlannerResponse = {
        success: true,
        project: {
          name: 'Fitness Tracker',
          description: 'A mobile app for tracking fitness goals',
          status: 'planning',
          priority: 'medium',
          tags: ['mobile', 'health'],
          estimated_total_minutes: 2400,
          estimated_total_hours: 40,
        },
        tasks: [],
      };

      mockApiClient.post.mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await service.generatePlan(request);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/planner/generate',
        request
      );
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockResponse);
    });

    it('should handle API errors', async () => {
      const request: PlannerRequest = {
        idea: 'Test idea',
        config: {
          provider: 'openai',
          create_milestones: false,
          max_milestones: 0,
          max_retries: 1,
        },
      };

      mockApiClient.post.mockResolvedValue({
        success: false,
        error: 'API key not configured',
      });

      const result = await service.generatePlan(request);

      expect(result.success).toBe(false);
      expect(result.error).toBe('API key not configured');
    });
  });

  describe('getProviders', () => {
    it('should fetch providers list', async () => {
      const mockProviders: ProvidersResponse = {
        providers: [
          {
            name: 'openai',
            display_name: 'OpenAI',
            models: [
              {
                name: 'gpt-4',
                display_name: 'GPT-4',
                is_default: true,
              },
            ],
            is_available: true,
            is_default: false,
          },
          {
            name: 'anthropic',
            display_name: 'Anthropic',
            models: [
              {
                name: 'claude-3-opus-20240229',
                display_name: 'Claude 3 Opus',
                is_default: true,
              },
            ],
            is_available: false,
            is_default: true,
          },
        ],
        default_provider: 'anthropic',
      };

      mockApiClient.get.mockResolvedValue({
        success: true,
        data: mockProviders,
      });

      const result = await service.getProviders();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/planner/providers');
      expect(result.success).toBe(true);
      expect(result.data?.providers).toHaveLength(2);
      expect(result.data?.providers[0].is_available).toBe(true);
      expect(result.data?.providers[1].is_available).toBe(false);
    });
  });

  describe('getDefaultConfig', () => {
    it('should fetch default configuration', async () => {
      const mockConfig = {
        default_config: {
          provider: 'anthropic',
          model_name: null,
          create_milestones: true,
          max_milestones: 5,
          max_retries: 2,
          retry_delay: 1.0,
        },
      };

      mockApiClient.get.mockResolvedValue({
        success: true,
        data: mockConfig,
      });

      const result = await service.getDefaultConfig();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/planner/config');
      expect(result.success).toBe(true);
      expect(result.data).toEqual(mockConfig);
    });
  });

  describe('getCacheStats', () => {
    it('should fetch cache statistics', async () => {
      const mockStats = {
        cache_size: 5,
        max_cache_size: 50,
        hits: 25,
        misses: 10,
        hit_rate: 0.714,
      };

      mockApiClient.get.mockResolvedValue({
        success: true,
        data: mockStats,
      });

      const result = await service.getCacheStats();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/planner/cache/stats');
      expect(result.success).toBe(true);
      expect(result.data?.hit_rate).toBe(0.714);
    });
  });

  describe('clearCache', () => {
    it('should clear the cache', async () => {
      const mockResponse = {
        success: true,
        message: 'Agent cache cleared successfully',
      };

      mockApiClient.post.mockResolvedValue({
        success: true,
        data: mockResponse,
      });

      const result = await service.clearCache();

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/planner/cache/clear',
        {}
      );
      expect(result.success).toBe(true);
      expect(result.data?.message).toBe('Agent cache cleared successfully');
    });
  });
});

describe('getPlannerService', () => {
  beforeEach(() => {
    // Reset the singleton instance
    vi.resetModules();
  });

  it('should return singleton instance', async () => {
    const { getPlannerService } = await import('./plannerService');
    const instance1 = getPlannerService();
    const instance2 = getPlannerService();
    
    expect(instance1).toBe(instance2);
  });

  it('should create ApiClient with 30 second timeout', async () => {
    vi.clearAllMocks();
    const { getPlannerService } = await import('./plannerService');
    getPlannerService();
    
    expect(ApiClient).toHaveBeenCalledWith('http://localhost:8000', 30000, 3);
  });
});