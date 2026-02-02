import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { MapPin, Search } from 'lucide-react'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DataTable } from '@/components/common/DataTable'
import { LocationMap, type MapLocation } from '@/components/charts/LocationMap'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  fetchLocations,
  fetchMissingLocations,
  updateLocation,
  geocodeAddress,
  createLocation,
} from '@/api/locations'
import type { LocationEntry } from '@/types'

export function LocationEditingPage() {
  const queryClient = useQueryClient()
  const [selectedLocation, setSelectedLocation] = useState<LocationEntry | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [coordinates, setCoordinates] = useState({ lat: '', lng: '' })

  const { data: locations, isLoading: locationsLoading } = useQuery({
    queryKey: ['locations'],
    queryFn: fetchLocations,
  })

  const { data: missingLocations, isLoading: missingLoading } = useQuery({
    queryKey: ['missing-locations'],
    queryFn: fetchMissingLocations,
  })

  const geocodeMutation = useMutation({
    mutationFn: geocodeAddress,
    onSuccess: (data) => {
      setCoordinates({
        lat: data.latitude.toString(),
        lng: data.longitude.toString(),
      })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ name, lat, lng }: { name: string; lat: number; lng: number }) =>
      updateLocation(name, { latitude: lat, longitude: lng }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      queryClient.invalidateQueries({ queryKey: ['missing-locations'] })
      setSelectedLocation(null)
      setCoordinates({ lat: '', lng: '' })
    },
  })

  const createMutation = useMutation({
    mutationFn: (location: LocationEntry) => createLocation(location),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['locations'] })
      queryClient.invalidateQueries({ queryKey: ['missing-locations'] })
      setCoordinates({ lat: '', lng: '' })
      setSearchQuery('')
    },
  })

  if (locationsLoading || missingLoading) return <LoadingPage />

  const handleLocationSelect = (location: LocationEntry) => {
    setSelectedLocation(location)
    setCoordinates({
      lat: location.Latitude?.toString() || '',
      lng: location.Longitude?.toString() || '',
    })
    setSearchQuery(location.Location)
  }

  const handleMapMarkerClick = (mapLoc: MapLocation) => {
    const location = locations?.find((l) => l.Location === mapLoc.name)
    if (location) {
      handleLocationSelect(location)
    }
  }

  const handleSearch = () => {
    if (searchQuery) {
      geocodeMutation.mutate(searchQuery)
    }
  }

  const handleSave = () => {
    if (selectedLocation && coordinates.lat && coordinates.lng) {
      updateMutation.mutate({
        name: selectedLocation.Location,
        lat: parseFloat(coordinates.lat),
        lng: parseFloat(coordinates.lng),
      })
    }
  }

  const handleCreateMissing = (locationName: string) => {
    if (coordinates.lat && coordinates.lng) {
      createMutation.mutate({
        Location: locationName,
        Latitude: parseFloat(coordinates.lat),
        Longitude: parseFloat(coordinates.lng),
      })
    }
  }

  // Prepare map locations
  const mapLocations: MapLocation[] = (locations ?? [])
    .filter((loc) => loc.Latitude != null && loc.Longitude != null)
    .map((loc) => ({
      name: loc.Location,
      latitude: loc.Latitude!,
      longitude: loc.Longitude!,
    }))

  // Add a marker for currently entered coordinates (for preview)
  const previewLocation: MapLocation | null =
    coordinates.lat && coordinates.lng && searchQuery
      ? {
          name: searchQuery,
          latitude: parseFloat(coordinates.lat),
          longitude: parseFloat(coordinates.lng),
          details: 'Preview - not saved yet',
        }
      : null

  const allMapLocations = previewLocation
    ? [...mapLocations.filter((l) => l.name !== previewLocation.name), previewLocation]
    : mapLocations

  const columns = [
    { key: 'Location', label: 'Location' },
    {
      key: 'Latitude',
      label: 'Latitude',
      render: (v: unknown) => (v ? Number(v).toFixed(4) : '-'),
    },
    {
      key: 'Longitude',
      label: 'Longitude',
      render: (v: unknown) => (v ? Number(v).toFixed(4) : '-'),
    },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Location Editing</h1>

      {/* Missing Locations */}
      {missingLocations && missingLocations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <MapPin className="h-5 w-5 text-orange-500" />
              Missing Locations ({missingLocations.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {missingLocations.map((loc) => (
                <Button
                  key={loc.location}
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery(loc.location)
                    setSelectedLocation({ Location: loc.location })
                    setCoordinates({ lat: '', lng: '' })
                  }}
                >
                  {loc.location}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Map */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Location Map</CardTitle>
        </CardHeader>
        <CardContent>
          <LocationMap
            locations={allMapLocations}
            height={400}
            selectedLocation={selectedLocation?.Location || searchQuery}
            onMarkerClick={handleMapMarkerClick}
          />
          <p className="text-sm text-muted-foreground mt-2">
            Click a marker to select and edit. Red marker shows current selection.
          </p>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Location List */}
        <Card>
          <CardHeader>
            <CardTitle>All Locations ({locations?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              data={(locations ?? []) as unknown as Record<string, unknown>[]}
              columns={columns}
              onRowClick={(row) => handleLocationSelect(row as unknown as LocationEntry)}
              className="max-h-96"
            />
          </CardContent>
        </Card>

        {/* Edit Form */}
        <Card>
          <CardHeader>
            <CardTitle>
              {selectedLocation ? `Edit: ${selectedLocation.Location}` : 'Add Location'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="search">Search Address</Label>
              <div className="flex gap-2">
                <Input
                  id="search"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter address to search"
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch} disabled={geocodeMutation.isPending}>
                  <Search className="h-4 w-4" />
                </Button>
              </div>
              {geocodeMutation.error && (
                <p className="text-sm text-destructive">Address not found</p>
              )}
              {geocodeMutation.data && (
                <p className="text-sm text-muted-foreground">
                  Found: {geocodeMutation.data.display_name}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="lat">Latitude</Label>
                <Input
                  id="lat"
                  type="number"
                  step="0.0001"
                  value={coordinates.lat}
                  onChange={(e) => setCoordinates({ ...coordinates, lat: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="lng">Longitude</Label>
                <Input
                  id="lng"
                  type="number"
                  step="0.0001"
                  value={coordinates.lng}
                  onChange={(e) => setCoordinates({ ...coordinates, lng: e.target.value })}
                />
              </div>
            </div>

            <div className="flex gap-2">
              {selectedLocation?.Latitude != null ? (
                <Button
                  onClick={handleSave}
                  disabled={updateMutation.isPending || !coordinates.lat || !coordinates.lng}
                  className="flex-1"
                >
                  {updateMutation.isPending ? 'Saving...' : 'Update Location'}
                </Button>
              ) : (
                <Button
                  onClick={() => handleCreateMissing(searchQuery || selectedLocation?.Location || '')}
                  disabled={
                    createMutation.isPending ||
                    !coordinates.lat ||
                    !coordinates.lng ||
                    (!searchQuery && !selectedLocation?.Location)
                  }
                  className="flex-1"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Location'}
                </Button>
              )}

              {(selectedLocation || searchQuery) && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setSelectedLocation(null)
                    setSearchQuery('')
                    setCoordinates({ lat: '', lng: '' })
                    geocodeMutation.reset()
                  }}
                >
                  Clear
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
