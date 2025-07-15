import { useState, useCallback } from 'react'
import type {
  PlannerRequest,
  PlannerResponse,
  ProvidersResponse,
  ConfigResponse,
  ErrorResponse,
  CacheStats,
} from '../types/api'

const API_BASE_URL = 'http://localhost:8000/api'

interface UsePlannerAPIReturn {
  loading: boolean
  error: string | null
  generatePlan: (request: PlannerRequest) => Promise<PlannerResponse | null>
  getProviders: () => Promise<ProvidersResponse | null>
  getConfig: () => Promise<ConfigResponse | null>
  getCacheStats: () => Promise<CacheStats | null>
  clearCache: () => Promise<{ success: boolean; message: string } | null>
  clearError: () => void
}

export function usePlannerAPI(): UsePlannerAPIReturn {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const handleRequest = useCallback(
    async <T>(
      url: string,
      options: RequestInit = {}
    ): Promise<T | null> => {
      setLoading(true)
      setError(null)

      try {
        const response = await fetch(`${API_BASE_URL}${url}`, {
          headers: {
            'Content-Type': 'application/json',
            ...options.headers,
          },
          ...options,
        })

        if (!response.ok) {
          const errorData: ErrorResponse = await response.json()
          throw new Error(errorData.error || `HTTP error! status: ${response.status}`)
        }

        const data: T = await response.json()
        return data
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred'
        setError(errorMessage)
        console.error('API request failed:', err)
        return null
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const generatePlan = useCallback(
    async (request: PlannerRequest): Promise<PlannerResponse | null> => {
      return handleRequest<PlannerResponse>('/planner/generate', {
        method: 'POST',
        body: JSON.stringify(request),
      })
    },
    [handleRequest]
  )

  const getProviders = useCallback(
    async (): Promise<ProvidersResponse | null> => {
      return handleRequest<ProvidersResponse>('/planner/providers')
    },
    [handleRequest]
  )

  const getConfig = useCallback(
    async (): Promise<ConfigResponse | null> => {
      return handleRequest<ConfigResponse>('/planner/config')
    },
    [handleRequest]
  )

  const getCacheStats = useCallback(
    async (): Promise<CacheStats | null> => {
      return handleRequest<CacheStats>('/planner/cache/stats')
    },
    [handleRequest]
  )

  const clearCache = useCallback(
    async (): Promise<{ success: boolean; message: string } | null> => {
      return handleRequest<{ success: boolean; message: string }>('/planner/cache/clear', {
        method: 'POST',
      })
    },
    [handleRequest]
  )

  return {
    loading,
    error,
    generatePlan,
    getProviders,
    getConfig,
    getCacheStats,
    clearCache,
    clearError,
  }
}