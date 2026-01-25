import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { BarChart } from '@/components/charts/BarChart'
import { Button } from '@/components/ui/button'
import { fetchSpending, fetchFilterOptions } from '@/api/spending'
import { formatCurrency, formatShortDate, getDateRange } from '@/lib/utils'
import type { SpendingEntry } from '@/types'

export function DetailedSpendingPage() {
  const defaultRange = getDateRange(30)
  const [startDate, setStartDate] = useState(defaultRange.start)
  const [endDate, setEndDate] = useState(defaultRange.end)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [selectedShops, setSelectedShops] = useState<string[]>([])

  const { data: filterOptions } = useQuery({
    queryKey: ['spending-filters'],
    queryFn: fetchFilterOptions,
  })

  const { data: spending, isLoading } = useQuery({
    queryKey: ['spending', startDate, endDate, selectedTags, selectedShops],
    queryFn: () =>
      fetchSpending({
        start_date: startDate,
        end_date: endDate,
        tags: selectedTags.length > 0 ? selectedTags : undefined,
        shops: selectedShops.length > 0 ? selectedShops : undefined,
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

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Detailed Spending</h1>

      <div className="flex gap-6">
        {/* Sidebar filters */}
        <div className="w-64 space-y-6 shrink-0">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />

          <div>
            <h3 className="font-medium mb-2">Tags</h3>
            <div className="space-y-1 max-h-40 overflow-auto">
              {filterOptions?.tags.slice(0, 10).map((tag) => (
                <label key={tag} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedTags.includes(tag)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedTags([...selectedTags, tag])
                      } else {
                        setSelectedTags(selectedTags.filter((t) => t !== tag))
                      }
                    }}
                  />
                  {tag}
                </label>
              ))}
            </div>
          </div>

          <div>
            <h3 className="font-medium mb-2">Shops</h3>
            <div className="space-y-1 max-h-40 overflow-auto">
              {filterOptions?.shops.slice(0, 10).map((shop) => (
                <label key={shop} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedShops.includes(shop)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedShops([...selectedShops, shop])
                      } else {
                        setSelectedShops(selectedShops.filter((s) => s !== shop))
                      }
                    }}
                  />
                  {shop}
                </label>
              ))}
            </div>
          </div>

          <Button
            variant="outline"
            onClick={() => {
              setSelectedTags([])
              setSelectedShops([])
            }}
          >
            Clear Filters
          </Button>
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
