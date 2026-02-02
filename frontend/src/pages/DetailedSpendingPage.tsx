import { useQuery } from '@tanstack/react-query'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { SearchableFilterList } from '@/components/common/SearchableFilterList'
import { BarChart } from '@/components/charts/BarChart'
import { LocationMap, type MapLocation } from '@/components/charts/LocationMap'
import { Button } from '@/components/ui/button'
import { fetchSpending, fetchFilterOptions } from '@/api/spending'
import { fetchLocations } from '@/api/locations'
import { formatCurrency, formatShortDate } from '@/lib/utils'
import { useSpendingFilters } from '@/hooks/usePersistedFilters'
import type { SpendingEntry } from '@/types'

export function DetailedSpendingPage() {
  const [filters, setFilter, clearFilters] = useSpendingFilters('detailed-spending', 30)

  const { data: filterOptions } = useQuery({
    queryKey: ['spending-filters', filters.startDate, filters.endDate],
    queryFn: () => fetchFilterOptions(filters.startDate, filters.endDate),
  })

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: fetchLocations,
  })

  const { data: spending, isLoading } = useQuery({
    queryKey: [
      'spending',
      filters.startDate,
      filters.endDate,
      filters.tags,
      filters.shops,
      filters.locations,
    ],
    queryFn: () =>
      fetchSpending({
        start_date: filters.startDate,
        end_date: filters.endDate,
        tags: filters.tags.length > 0 ? filters.tags : undefined,
        shops: filters.shops.length > 0 ? filters.shops : undefined,
        locations: filters.locations.length > 0 ? filters.locations : undefined,
      }),
  })

  if (isLoading) return <LoadingPage />

  // Prepare chart data
  const byTag = spending
    ? Object.entries(
        spending.reduce((acc: Record<string, number>, entry: SpendingEntry) => {
          const tag = entry.Tag || 'Untagged'
          acc[tag] = (acc[tag] || 0) + entry.Cost
          return acc
        }, {})
      ).map(([name, value]) => ({ name, value }))
    : []

  const byShop = spending
    ? Object.entries(
        spending.reduce((acc: Record<string, number>, entry: SpendingEntry) => {
          const shop = entry.Shop || 'Unknown'
          acc[shop] = (acc[shop] || 0) + entry.Cost
          return acc
        }, {})
      ).map(([name, value]) => ({ name, value }))
    : []

  // Prepare map data - aggregate spending by location
  const spendingByLocation = spending
    ? spending.reduce((acc: Record<string, number>, entry: SpendingEntry) => {
        if (entry.Location) {
          acc[entry.Location] = (acc[entry.Location] || 0) + entry.Cost
        }
        return acc
      }, {})
    : {}

  const mapLocations: MapLocation[] = (locations ?? [])
    .filter((loc) => loc.Latitude != null && loc.Longitude != null)
    .map((loc) => ({
      name: loc.Location,
      latitude: loc.Latitude!,
      longitude: loc.Longitude!,
      value: spendingByLocation[loc.Location] || 0,
    }))
    .filter((loc) => loc.value > 0) // Only show locations with spending

  const totalCost = spending?.reduce((sum, e) => sum + e.Cost, 0) ?? 0

  const columns = [
    { key: 'Date', label: 'Date', render: (v: unknown) => formatShortDate(String(v)) },
    { key: 'Item', label: 'Item' },
    { key: 'Cost', label: 'Cost', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'Shop', label: 'Shop' },
    { key: 'Location', label: 'Location' },
    { key: 'Tag', label: 'Tag' },
    { key: 'Category', label: 'Category' },
  ]

  const toggleArrayFilter = (
    key: 'tags' | 'shops' | 'locations',
    value: string,
    checked: boolean
  ) => {
    const current = filters[key]
    if (checked) {
      setFilter(key, [...current, value])
    } else {
      setFilter(key, current.filter((v) => v !== value))
    }
  }

  const sortAlphabetically = (a: string, b: string): number => a.localeCompare(b)
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Detailed Spending</h1>

      <div className="flex gap-6">
        {/* Sidebar filters */}
        <div className="w-64 space-y-6 shrink-0">
          <DateRangePicker
            startDate={filters.startDate}
            endDate={filters.endDate}
            onStartDateChange={(date) => setFilter('startDate', date)}
            onEndDateChange={(date) => setFilter('endDate', date)}
          />

          <SearchableFilterList
            title="Tags"
            options={filterOptions?.tags.sort(sortAlphabetically) ?? []}
            selected={filters.tags}
            onChange={(value, checked) => toggleArrayFilter('tags', value, checked)}
          />

          <SearchableFilterList
            title="Shops"
            options={filterOptions?.shops.sort(sortAlphabetically) ?? []}
            selected={filters.shops}
            onChange={(value, checked) => toggleArrayFilter('shops', value, checked)}
          />

          <SearchableFilterList
            title="Locations"
            options={filterOptions?.locations.sort(sortAlphabetically) ?? []}
            selected={filters.locations}
            onChange={(value, checked) => toggleArrayFilter('locations', value, checked)}
          />

          <Button variant="outline" onClick={clearFilters}>
            Clear Filters
          </Button>

          <div className="text-sm text-muted-foreground pt-2 border-t">
            Filters are saved automatically
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 space-y-6">
          <div className="text-lg font-semibold">
            Total: {formatCurrency(totalCost)} ({spending?.length ?? 0} transactions)
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <BarChart data={byTag} title="Spending by Tag" maxItems={15} />
            </div>
            <div className="border rounded-lg p-4">
              <BarChart
                data={byShop}
                title="Spending by Shop"
                maxItems={15}
                color="#10b981"
              />
            </div>
          </div>

          {/* Map visualization */}
          {mapLocations.length > 0 && (
            <div className="border rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-4">Spending by Location</h3>
              <LocationMap
                locations={mapLocations}
                height={400}
                showValues={true}
                onMarkerClick={(loc) => {
                  toggleArrayFilter('locations', loc.name, !filters.locations.includes(loc.name))
                }}
              />
              <p className="text-sm text-muted-foreground mt-2">
                Click markers to filter by location
              </p>
            </div>
          )}

          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Transactions</h3>
            <DataTable
              data={(spending ?? []) as unknown as Record<string, unknown>[]}
              columns={columns}
              className="max-h-96"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
