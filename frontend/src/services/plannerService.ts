/**
 * Planner-specific API operations for AI project generation
 */
import { ApiClient, type ApiResponse } from './api';
import type {
  PlannerRequest,
  PlannerResponse,
  ProvidersResponse,
  ConfigResponse,
  CacheStats,
} from '../types/api';

export class PlannerService {
  private apiClient: ApiClient;

  constructor(apiClient?: ApiClient) {
    this.apiClient = apiClient || new ApiClient();
  }

  /**
   * Generate a project plan from natural language description
   */
  async generatePlan(request: PlannerRequest): Promise<ApiResponse<PlannerResponse>> {
    return this.apiClient.post<PlannerResponse>('/api/planner/generate', request);
  }

  /**
   * Get available AI providers and their models
   */
  async getProviders(): Promise<ApiResponse<ProvidersResponse>> {
    return this.apiClient.get<ProvidersResponse>('/api/planner/providers');
  }

  /**
   * Get default planner configuration
   */
  async getDefaultConfig(): Promise<ApiResponse<ConfigResponse>> {
    return this.apiClient.get<ConfigResponse>('/api/planner/config');
  }

  /**
   * Get cache statistics for debugging and monitoring
   */
  async getCacheStats(): Promise<ApiResponse<CacheStats>> {
    return this.apiClient.get<CacheStats>('/api/planner/cache/stats');
  }

  /**
   * Clear the agent cache
   */
  async clearCache(): Promise<ApiResponse<{ success: boolean; message: string }>> {
    return this.apiClient.post<{ success: boolean; message: string }>('/api/planner/cache/clear', {});
  }
}

// Export singleton instance
let plannerServiceInstance: PlannerService | null = null;

export const getPlannerService = (): PlannerService => {
  if (!plannerServiceInstance) {
    // Create API client with 30 second timeout for AI generation
    const apiClient = new ApiClient('http://localhost:8000', 30000, 3);
    plannerServiceInstance = new PlannerService(apiClient);
  }
  return plannerServiceInstance;
};