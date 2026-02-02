import { useEffect, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Tooltip, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default marker icons in Leaflet with bundlers
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

export interface MapLocation {
  name: string
  latitude: number
  longitude: number
  value?: number
  details?: string
}

interface LocationMapProps {
  locations: MapLocation[]
  height?: number
  onMarkerClick?: (location: MapLocation) => void
  selectedLocation?: string
  showValues?: boolean
  className?: string
}

// Component to handle map bounds fitting
function MapBoundsController({
  locations,
  selectedLocation,
}: {
  locations: MapLocation[]
  selectedLocation?: string
}) {
  const map = useMap()

  useEffect(() => {
    if (locations.length === 0) return

    // If there's a selected location, center on it with a closer zoom
    if (selectedLocation) {
      const selected = locations.find((loc) => loc.name === selectedLocation)
      if (selected) {
        map.setView([selected.latitude, selected.longitude], 14)
        return
      }
    }

    // Otherwise, fit bounds to show all markers
    if (locations.length === 1) {
      map.setView([locations[0].latitude, locations[0].longitude], 14)
    } else {
      const bounds = L.latLngBounds(
        locations.map((loc) => [loc.latitude, loc.longitude])
      )
      map.fitBounds(bounds, { padding: [50, 50] })
    }
  }, [map, locations, selectedLocation])

  return null
}

// Create a custom icon with different colors
function createIcon(isSelected: boolean, hasValue: boolean) {
  const color = isSelected ? '#ef4444' : hasValue ? '#3b82f6' : '#6b7280'

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">
        <path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 9.4 12.5 28.5 12.5 28.5S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z" fill="${color}"/>
        <circle cx="12.5" cy="12.5" r="5" fill="white"/>
      </svg>
    `,
    iconSize: [25, 41],
    iconAnchor: [12.5, 41],
    popupAnchor: [0, -41],
  })
}

export function LocationMap({
  locations,
  height = 400,
  onMarkerClick,
  selectedLocation,
  showValues = false,
  className = '',
}: LocationMapProps) {
  // Filter out locations without valid coordinates
  const validLocations = useMemo(
    () =>
      locations.filter(
        (loc) =>
          loc.latitude != null &&
          loc.longitude != null &&
          !isNaN(loc.latitude) &&
          !isNaN(loc.longitude)
      ),
    [locations]
  )

  // Calculate initial center (will be adjusted by MapBoundsController)
  const initialCenter: [number, number] = useMemo(() => {
    if (validLocations.length === 0) {
      return [-33.8688, 151.2093] // Sydney as default
    }
    const avgLat =
      validLocations.reduce((sum, loc) => sum + loc.latitude, 0) /
      validLocations.length
    const avgLng =
      validLocations.reduce((sum, loc) => sum + loc.longitude, 0) /
      validLocations.length
    return [avgLat, avgLng]
  }, [validLocations])

  // Format currency for tooltip
  const formatValue = (value: number | undefined) => {
    if (value === undefined) return ''
    return new Intl.NumberFormat('en-AU', {
      style: 'currency',
      currency: 'AUD',
    }).format(value)
  }

  return (
    <div className={`rounded-lg overflow-hidden border ${className}`} style={{ height }}>
      <MapContainer
        center={initialCenter}
        zoom={10}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <MapBoundsController
          locations={validLocations}
          selectedLocation={selectedLocation}
        />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {validLocations.map((location) => (
          <Marker
            key={location.name}
            position={[location.latitude, location.longitude]}
            icon={createIcon(
              location.name === selectedLocation,
              location.value !== undefined && location.value > 0
            )}
            eventHandlers={{
              click: () => onMarkerClick?.(location),
            }}
          >
            <Tooltip direction="top" offset={[0, -35]} opacity={0.95}>
              <div className="font-medium">{location.name}</div>
              {showValues && location.value !== undefined && (
                <div className="text-sm text-gray-600">
                  {formatValue(location.value)}
                </div>
              )}
              {location.details && (
                <div className="text-xs text-gray-500 mt-1">
                  {location.details}
                </div>
              )}
              <div className="text-xs text-gray-400 mt-1">
                {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
              </div>
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>
    </div>
  )
}
