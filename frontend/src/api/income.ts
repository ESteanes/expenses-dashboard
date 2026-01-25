import { apiClient } from './client'
import type { IncomeEntry, IncomeSummary, IncomeFilterOptions } from '../types'

interface IncomeFilters {
  start_date?: string
  end_date?: string
  employers?: string[]
  descriptions?: string[]
  financial_years?: string[]
}

export async function fetchIncome(filters?: IncomeFilters): Promise<IncomeEntry[]> {
  const params = new URLSearchParams()
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  filters?.employers?.forEach(e => params.append('employers', e))
  filters?.descriptions?.forEach(d => params.append('descriptions', d))
  filters?.financial_years?.forEach(fy => params.append('financial_years', fy))

  const response = await apiClient.get<IncomeEntry[]>('/income', { params })
  return response.data
}

export async function fetchIncomeSummary(
  startDate?: string,
  endDate?: string
): Promise<IncomeSummary> {
  const params = new URLSearchParams()
  if (startDate) params.append('start_date', startDate)
  if (endDate) params.append('end_date', endDate)

  const response = await apiClient.get<IncomeSummary>('/income/summary', { params })
  return response.data
}

export async function fetchIncomeFilterOptions(): Promise<IncomeFilterOptions> {
  const response = await apiClient.get<IncomeFilterOptions>('/income/filters')
  return response.data
}

export async function createIncomeEntry(entry: Partial<IncomeEntry>): Promise<IncomeEntry> {
  const response = await apiClient.post<IncomeEntry>('/income', {
    gross_income: entry['Gross Income'],
    salary_sacrifice: entry['Salary Sacrifice'] || 0,
    tax: entry.Tax || 0,
    income: entry.Income,
    date: entry.Date,
    employer: entry.Employer,
    description: entry.Description,
    taxable: entry.Taxable,
    received_in_bank_account: entry['Received in bank account'] || 'Yes',
    comment: entry.Comment,
  })
  return response.data
}

export async function deleteIncomeEntry(index: number): Promise<void> {
  await apiClient.delete(`/income/${index}`)
}
