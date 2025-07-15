/**
 * Base API client with authentication and error handling
 */

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
  status?: number;
}

export interface ApiError {
  message: string;
  status: number;
  details?: string;
}

export class ApiClient {
  private baseUrl: string;
  private timeout: number;
  private retryAttempts: number;

  constructor(baseUrl: string = 'http://localhost:8000', timeout: number = 10000, retryAttempts: number = 3) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
    this.retryAttempts = retryAttempts;
  }

  /**
   * Make HTTP request with error handling and retry logic
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    attempt: number = 1
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };

    const config: RequestInit = {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      signal: AbortSignal.timeout(this.timeout),
    };

    try {
      console.log(`ApiClient: Fetching ${url}`, config);
      const response = await fetch(url, config);
      console.log(`ApiClient: Response status ${response.status} for ${url}`);
      
      // Handle successful response
      if (response.ok) {
        const data = await response.json();
        console.log(`ApiClient: Success response from ${url}:`, data);
        return {
          data,
          success: true,
        };
      }
      
      // Handle error responses
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let errorDetails = '';
      
      try {
        const errorData = await response.json();
        // Handle FastAPI error format with nested detail object
        if (errorData.detail && typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.error || errorData.detail.message || errorMessage;
          errorDetails = errorData.detail.details || '';
        } else {
          errorMessage = errorData.detail || errorData.error || errorMessage;
          errorDetails = errorData.details || '';
        }
      } catch {
        // If error response is not JSON, use status text
      }
      
      const apiError: ApiError = {
        message: errorMessage,
        status: response.status,
        details: errorDetails,
      };
      
      // Don't retry for client errors (4xx)
      if (response.status >= 400 && response.status < 500) {
        console.log(`ApiClient: Client error for ${url}:`, apiError);
        return {
          data: null as T,
          success: false,
          error: apiError.message,
        };
      }
      
      // Don't retry for 500 errors with specific error codes (configuration issues)
      if (response.status === 500 && apiError.details && typeof apiError.details === 'object') {
        console.log(`ApiClient: Server configuration error for ${url}, not retrying`);
        return {
          data: null as T,
          success: false,
          error: apiError.message,
        };
      }
      
      // Retry for other server errors (5xx) and network errors
      if (attempt < this.retryAttempts) {
        console.warn(`Request failed, retrying... (${attempt}/${this.retryAttempts})`);
        await this.delay(Math.pow(2, attempt) * 1000); // Exponential backoff
        return this.request<T>(endpoint, options, attempt + 1);
      }
      
      return {
        data: null as T,
        success: false,
        error: apiError.message,
      };
      
    } catch (error) {
      console.error(`ApiClient: Exception for ${url}:`, error);
      // Handle network errors, timeouts, etc.
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          const message = 'Request timeout';
          if (attempt < this.retryAttempts) {
            console.warn(`Request timeout, retrying... (${attempt}/${this.retryAttempts})`);
            await this.delay(Math.pow(2, attempt) * 1000);
            return this.request<T>(endpoint, options, attempt + 1);
          }
          return {
            data: null as T,
            success: false,
            error: message,
          };
        }
        
        if (attempt < this.retryAttempts) {
          console.warn(`Network error, retrying... (${attempt}/${this.retryAttempts})`);
          await this.delay(Math.pow(2, attempt) * 1000);
          return this.request<T>(endpoint, options, attempt + 1);
        }
        
        return {
          data: null as T,
          success: false,
          error: error.message,
        };
      }
      
      return {
        data: null as T,
        success: false,
        error: 'An unexpected error occurred',
      };
    }
  }

  /**
   * Utility method for delay
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    let url = endpoint;
    
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      const queryString = searchParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
    }
    
    return this.request<T>(url, { method: 'GET' });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  /**
   * Health check endpoint
   */
  async health(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.get<{ status: string; service: string }>('/health');
  }
}

// Create and export default API client instance
export const apiClient = new ApiClient();