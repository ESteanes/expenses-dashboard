import { apiClient } from './client'
import type { LocationEntry, GeocodeResult } from '../types'

export async function fetchLocations(): Promise<LocationEntry[]> {
  const response = await apiClient.get<LocationEntry[]>('/locations')
  return response.data
}

export async function fetchMissingLocations(): Promise<{ location: string }[]> {
  const response = await apiClient.get<{ location: string }[]>('/locations/missing')
  return response.data
}

export async function createLocation(location: LocationEntry): Promise<LocationEntry> {
  const response = await apiClient.post<LocationEntry>('/locations', location)
  return response.data
}

export async function updateLocation(
  locationName: string,
  update: { latitude?: number; longitude?: number }
): Promise<LocationEntry> {
  const response = await apiClient.put<LocationEntry>(
    `/locations/${encodeURIComponent(locationName)}`,
    update
  )
  return response.data
}

export async function geocodeAddress(address: string): Promise<GeocodeResult> {
  const response = await apiClient.post<GeocodeResult>('/locations/geocode', { address })
  return response.data
}
