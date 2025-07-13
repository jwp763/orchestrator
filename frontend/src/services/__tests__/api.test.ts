/**
 * Tests for the base ApiClient class
 * 
 * Tests HTTP methods, error handling, retry logic, and timeout behavior
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ApiClient, type ApiResponse, type ApiError } from '../api';

// Mock fetch for testing
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('ApiClient', () => {
  let apiClient: ApiClient;
  
  beforeEach(() => {
    apiClient = new ApiClient('http://test-api.com', 5000, 2);
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with default values', () => {
      const client = new ApiClient();
      expect(client).toBeInstanceOf(ApiClient);
    });

    it('should initialize with custom values', () => {
      const client = new ApiClient('http://custom.com', 3000, 5);
      expect(client).toBeInstanceOf(ApiClient);
    });
  });

  describe('HTTP Methods', () => {
    describe('GET requests', () => {
      it('should make successful GET request', async () => {
        const mockData = { id: 1, name: 'Test' };
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockData),
        });

        const response = await apiClient.get<typeof mockData>('/test');

        expect(response.success).toBe(true);
        expect(response.data).toEqual(mockData);
        expect(response.error).toBeUndefined();
        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test',
          expect.objectContaining({
            method: 'GET',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            }),
          })
        );
      });

      it('should handle GET request with query parameters', async () => {
        const mockData = { results: [] };
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockData),
        });

        const params = { page: 1, limit: 10, status: 'active' };
        await apiClient.get('/test', params);

        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test?page=1&limit=10&status=active',
          expect.any(Object)
        );
      });

      it('should filter out null and undefined query parameters', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({}),
        });

        const params = { page: 1, limit: null, status: undefined, active: 'true' };
        await apiClient.get('/test', params);

        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test?page=1&active=true',
          expect.any(Object)
        );
      });
    });

    describe('POST requests', () => {
      it('should make successful POST request with data', async () => {
        const mockData = { id: 1, name: 'Created' };
        const requestData = { name: 'Test Item' };
        
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockData),
        });

        const response = await apiClient.post<typeof mockData>('/test', requestData);

        expect(response.success).toBe(true);
        expect(response.data).toEqual(mockData);
        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test',
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(requestData),
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            }),
          })
        );
      });

      it('should make POST request without data', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({}),
        });

        await apiClient.post('/test');

        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test',
          expect.objectContaining({
            method: 'POST',
            body: undefined,
          })
        );
      });
    });

    describe('PUT requests', () => {
      it('should make successful PUT request', async () => {
        const mockData = { id: 1, name: 'Updated' };
        const requestData = { name: 'Updated Item' };
        
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockData),
        });

        const response = await apiClient.put<typeof mockData>('/test/1', requestData);

        expect(response.success).toBe(true);
        expect(response.data).toEqual(mockData);
        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test/1',
          expect.objectContaining({
            method: 'PUT',
            body: JSON.stringify(requestData),
          })
        );
      });
    });

    describe('DELETE requests', () => {
      it('should make successful DELETE request', async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

        const response = await apiClient.delete('/test/1');

        expect(response.success).toBe(true);
        expect(mockFetch).toHaveBeenCalledWith(
          'http://test-api.com/test/1',
          expect.objectContaining({
            method: 'DELETE',
          })
        );
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle 4xx client errors without retry', async () => {
      const errorResponse = { detail: 'Not found' };
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: () => Promise.resolve(errorResponse),
      });

      const response = await apiClient.get('/not-found');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Not found');
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should handle 5xx server errors with retry', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.resolve({ detail: 'Server error' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      const response = await apiClient.get('/server-error');

      expect(response.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('should exhaust retry attempts for persistent server errors', async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: () => Promise.resolve({ detail: 'Persistent server error' }),
      });

      const response = await apiClient.get('/persistent-error');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Persistent server error');
      expect(mockFetch).toHaveBeenCalledTimes(2); // 1 initial + 1 retry
    });

    it('should handle non-JSON error responses', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.reject(new Error('Not JSON')),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: () => Promise.reject(new Error('Not JSON')),
        });

      const response = await apiClient.get('/non-json-error');

      expect(response.success).toBe(false);
      expect(response.error).toBe('HTTP 500: Internal Server Error');
    });

    it('should handle network errors with retry', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      const response = await apiClient.get('/network-error');

      expect(response.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('should handle timeout errors with retry', async () => {
      const abortError = new Error('The operation was aborted');
      abortError.name = 'AbortError';
      
      mockFetch
        .mockRejectedValueOnce(abortError)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      const response = await apiClient.get('/timeout-error');

      expect(response.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });

    it('should handle persistent timeout errors', async () => {
      const abortError = new Error('The operation was aborted');
      abortError.name = 'AbortError';
      
      mockFetch.mockRejectedValue(abortError);

      const response = await apiClient.get('/persistent-timeout');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Request timeout');
      expect(mockFetch).toHaveBeenCalledTimes(2); // 1 initial + 1 retry
    });

    it('should handle unexpected errors', async () => {
      mockFetch.mockRejectedValueOnce('Some weird error');

      const response = await apiClient.get('/unexpected-error');

      expect(response.success).toBe(false);
      expect(response.error).toBe('An unexpected error occurred');
    });
  });

  describe('Health Check', () => {
    it('should perform health check', async () => {
      const healthData = { status: 'healthy', service: 'api' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(healthData),
      });

      const response = await apiClient.health();

      expect(response.success).toBe(true);
      expect(response.data).toEqual(healthData);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://test-api.com/health',
        expect.objectContaining({
          method: 'GET',
        })
      );
    });
  });

  describe('Request Configuration', () => {
    it('should set timeout signal', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      await apiClient.get('/test');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          signal: expect.any(AbortSignal),
        })
      );
    });

    it('should merge custom headers with defaults', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      // Access private request method via any cast for testing
      const apiClientAny = apiClient as any;
      await apiClientAny.request('/test', {
        headers: {
          'Authorization': 'Bearer token',
          'Custom-Header': 'value',
        },
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer token',
            'Custom-Header': 'value',
          }),
        })
      );
    });
  });

  describe('Retry Logic', () => {
    it('should implement exponential backoff', async () => {
      const delaySpy = vi.spyOn(apiClient as any, 'delay');
      delaySpy.mockResolvedValue(undefined);

      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      await apiClient.get('/retry-test');

      // Should call delay with exponential backoff: 2^1 * 1000 for first retry
      expect(delaySpy).toHaveBeenCalledWith(2000);
      expect(delaySpy).toHaveBeenCalledTimes(1);
      
      delaySpy.mockRestore();
    });
  });
});