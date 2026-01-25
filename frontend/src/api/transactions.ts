import { apiClient } from './client'
import type { Transaction } from '../types'

export async function fetchTransactions(
  startDate?: string,
  endDate?: string
): Promise<Transaction[]> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const response = await apiClient.get<Transaction[]>('/transactions', { params })
  return response.data
}

export async function fetchUncategorizedTransactions(
  startDate?: string,
  endDate?: string
): Promise<Transaction[]> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const response = await apiClient.get<Transaction[]>('/transactions/uncategorized', { params })
  return response.data
}

export async function fetchRawTransactions(
  startDate?: string,
  endDate?: string
): Promise<Transaction[]> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const response = await apiClient.get<Transaction[]>('/transactions/raw', { params })
  return response.data
}
