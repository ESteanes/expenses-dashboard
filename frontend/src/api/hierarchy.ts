import { apiClient } from './client'
import type { HierarchyData, CategoryEntry, SubCategoryEntry, ItemEntry } from '../types'

export async function fetchHierarchy(): Promise<HierarchyData> {
  const response = await apiClient.get<HierarchyData>('/hierarchy/all')
  return response.data
}

export async function fetchCategories(): Promise<CategoryEntry[]> {
  const response = await apiClient.get<CategoryEntry[]>('/hierarchy/categories')
  return response.data
}

export async function fetchSubCategories(): Promise<SubCategoryEntry[]> {
  const response = await apiClient.get<SubCategoryEntry[]>('/hierarchy/subcategories')
  return response.data
}

export async function fetchItems(): Promise<ItemEntry[]> {
  const response = await apiClient.get<ItemEntry[]>('/hierarchy/items')
  return response.data
}

export async function updateCategories(entries: CategoryEntry[]): Promise<void> {
  await apiClient.put('/hierarchy/categories', { entries })
}

export async function updateSubCategories(entries: SubCategoryEntry[]): Promise<void> {
  await apiClient.put('/hierarchy/subcategories', { entries })
}

export async function updateItems(entries: ItemEntry[]): Promise<void> {
  await apiClient.put('/hierarchy/items', { entries })
}
