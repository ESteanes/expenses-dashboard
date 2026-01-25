import { apiClient } from './client'
import type { SystemStatus } from '../types'

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const response = await apiClient.get<SystemStatus>('/system/status')
  return response.data
}

export async function refreshData(): Promise<{ success: boolean; timestamp: string }> {
  const response = await apiClient.post<{ success: boolean; timestamp: string }>('/system/refresh')
  return response.data
}
