import { useState, useEffect, useCallback } from 'react'

/**
 * Hook for persisting filter state in localStorage.
 * Filters persist when navigating away and back to a page.
 * Each page has its own storage key.
 */
export function usePersistedFilters<T extends Record<string, unknown>>(
  pageKey: string,
  defaultValues: T
): [T, <K extends keyof T>(key: K, value: T[K]) => void, () => void] {
  const storageKey = `filters:${pageKey}`

  // Initialize state from localStorage or defaults
  const [filters, setFilters] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(storageKey)
      if (stored) {
        return { ...defaultValues, ...JSON.parse(stored) }
      }
    } catch (e) {
      console.warn('Failed to load filters from localStorage:', e)
    }
    return defaultValues
  })

  // Save to localStorage whenever filters change
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(filters))
    } catch (e) {
      console.warn('Failed to save filters to localStorage:', e)
    }
  }, [storageKey, filters])

  const setFilter = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }, [])

  const clearFilters = useCallback(() => {
    setFilters(defaultValues)
    try {
      localStorage.removeItem(storageKey)
    } catch (e) {
      console.warn('Failed to clear filters from localStorage:', e)
    }
  }, [defaultValues, storageKey])

  return [filters, setFilter, clearFilters]
}

/**
 * Get default date range for filter initialization
 */
function getDefaultDateRange(days: number) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  return {
    start: start.toISOString().split('T')[0],
    end: end.toISOString().split('T')[0],
  }
}

/**
 * Pre-configured hook for spending pages with common filter pattern
 */
export function useSpendingFilters(pageKey: string, defaultDays = 30) {
  const range = getDefaultDateRange(defaultDays)

  return usePersistedFilters(pageKey, {
    startDate: range.start,
    endDate: range.end,
    tags: [] as string[],
    shops: [] as string[],
    locations: [] as string[],
    categories: [] as string[],
  })
}

/**
 * Pre-configured hook for recording expenses page
 */
export function useRecordingFilters() {
  const range = getDefaultDateRange(30)

  return usePersistedFilters('recording-expenses', {
    startDate: range.start,
    endDate: range.end,
  })
}

/**
 * Pre-configured hook for income page
 */
export function useIncomeFilters() {
  const range = getDefaultDateRange(365)

  return usePersistedFilters('income', {
    startDate: range.start,
    endDate: range.end,
    employers: [] as string[],
    financialYears: [] as string[],
  })
}
