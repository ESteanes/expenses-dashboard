import { apiClient } from './client'
import type { SpendingEntry, SpendingSummary, SpendingFilters, FilterOptions } from '../types'

export async function fetchSpending(filters?: SpendingFilters): Promise<SpendingEntry[]> {
  const params = new URLSearchParams()
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  filters?.tags?.forEach(t => params.append('tags', t))
  filters?.shops?.forEach(s => params.append('shops', s))
  filters?.locations?.forEach(l => params.append('locations', l))
  filters?.categories?.forEach(c => params.append('categories', c))
  filters?.sub_categories?.forEach(sc => params.append('sub_categories', sc))

  const response = await apiClient.get<SpendingEntry[]>('/spending', { params })
  return response.data
}

export async function fetchSpendingSummary(
  startDate?: string,
  endDate?: string
): Promise<SpendingSummary> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const response = await apiClient.get<SpendingSummary>('/spending/summary', { params })
  return response.data
}

export async function fetchRecentSpending(days = 30): Promise<SpendingSummary> {
  const response = await apiClient.get<SpendingSummary>('/spending/recent', {
    params: { days }
  })
  return response.data
}

export async function fetchFilterOptions(): Promise<FilterOptions> {
  const response = await apiClient.get<FilterOptions>('/spending/filters')
  return response.data
}

export async function createSpendingEntry(entry: Partial<SpendingEntry>): Promise<SpendingEntry> {
  const response = await apiClient.post<SpendingEntry>('/spending', {
    item: entry.Item,
    cost: entry.Cost,
    quantity: entry.Quantity,
    measure: entry.Measure,
    location: entry.Location,
    shop: entry.Shop,
    details: entry.Details,
    tag: entry.Tag,
    date: entry.Date,
    receipt_ref: entry['Receipt Ref'],
    transaction_id: entry.transactionId,
  })
  return response.data
}

export async function updateSpendingEntry(
  index: number,
  entry: Partial<SpendingEntry>
): Promise<SpendingEntry> {
  const response = await apiClient.put<SpendingEntry>(`/spending/${index}`, {
    item: entry.Item,
    cost: entry.Cost,
    quantity: entry.Quantity,
    measure: entry.Measure,
    location: entry.Location,
    shop: entry.Shop,
    details: entry.Details,
    tag: entry.Tag,
    date: entry.Date,
    receipt_ref: entry['Receipt Ref'],
  })
  return response.data
}

export async function deleteSpendingEntry(index: number): Promise<void> {
  await apiClient.delete(`/spending/${index}`)
}
