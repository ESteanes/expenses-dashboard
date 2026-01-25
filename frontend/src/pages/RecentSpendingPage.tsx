import { useQuery } from '@tanstack/react-query'
import { MetricCard } from '@/components/common/MetricCard'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { BarChart } from '@/components/charts/BarChart'
import { fetchRecentSpending, fetchSpending } from '@/api/spending'
import { formatCurrency, getDateRange } from '@/lib/utils'
import type { SpendingEntry } from '@/types'

export function RecentSpendingPage() {
  const { start } = getDateRange(30)

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['recent-spending-summary'],
    queryFn: () => fetchRecentSpending(30),
  })

  const { data: spending, isLoading: spendingLoading } = useQuery({
    queryKey: ['recent-spending', start],
    queryFn: () => fetchSpending({ start_date: start }),
  })

  if (summaryLoading || spendingLoading) return <LoadingPage />

  // Prepare chart data
  const byTag = summary?.by_tag
    ? Object.entries(summary.by_tag).map(([name, value]) => ({ name, value }))
    : []

  const byShop = summary?.by_shop
    ? Object.entries(summary.by_shop).map(([name, value]) => ({ name, value }))
    : []

  const byLocation = spending
    ? Object.entries(
        spending.reduce((acc: Record<string, number>, entry: SpendingEntry) => {
          const loc = entry.Location || 'Unknown'
          acc[loc] = (acc[loc] || 0) + entry.Cost
          return acc
        }, {})
      ).map(([name, value]) => ({ name, value }))
    : []

  // Calculate category breakdowns
  const byCategory = summary?.by_category || {}
  const discretionary = byCategory['Wants'] || byCategory['Discretionary'] || 0
  const necessary = byCategory['Needs'] || byCategory['Necessary'] || 0
  const misc = Object.entries(byCategory)
    .filter(([key]) => !['Wants', 'Discretionary', 'Needs', 'Necessary'].includes(key))
    .reduce((sum, [, val]) => sum + val, 0)

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Recent Spending (Past 30 Days)</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Cost"
          value={formatCurrency(summary?.total_cost ?? 0)}
          className="bg-blue-50"
        />
        <MetricCard
          label="Discretionary/Wants"
          value={formatCurrency(discretionary)}
        />
        <MetricCard
          label="Miscellaneous"
          value={formatCurrency(misc)}
        />
        <MetricCard
          label="Necessary/Needs"
          value={formatCurrency(necessary)}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="border rounded-lg p-4">
          <BarChart
            data={byTag}
            title="Cost by Tag (Top 20)"
            maxItems={20}
            color="#3b82f6"
          />
        </div>
        <div className="border rounded-lg p-4">
          <BarChart
            data={byShop}
            title="Cost by Shop (Top 20)"
            maxItems={20}
            color="#10b981"
          />
        </div>
      </div>

      <div className="border rounded-lg p-4">
        <BarChart
          data={byLocation}
          title="Cost by Location (Top 20)"
          maxItems={20}
          color="#f59e0b"
          height={350}
        />
      </div>
    </div>
  )
}
