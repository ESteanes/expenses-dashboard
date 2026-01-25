import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { RefreshCw } from 'lucide-react'
import { MetricCard } from '@/components/common/MetricCard'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { fetchSystemStatus, refreshData } from '@/api/system'
import { formatDate } from '@/lib/utils'

export function HomePage() {
  const queryClient = useQueryClient()

  const { data: status, isLoading, error } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchSystemStatus,
  })

  const refreshMutation = useMutation({
    mutationFn: refreshData,
    onSuccess: () => {
      queryClient.invalidateQueries()
    },
  })

  if (isLoading) return <LoadingPage />

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-destructive">Error loading status: {String(error)}</p>
        <Button onClick={() => queryClient.invalidateQueries()} className="mt-4">
          Retry
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Home</h1>
        <Button
          onClick={() => refreshMutation.mutate()}
          disabled={refreshMutation.isPending}
        >
          <RefreshCw className={refreshMutation.isPending ? 'animate-spin' : ''} />
          Refresh Data
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Last Refresh"
          value={status ? formatDate(status.timestamp, 'dd MMM yyyy HH:mm') : '-'}
        />
        <MetricCard
          label="Uncategorized Transactions"
          value={status?.counts.spending ?? 0}
          description="Transactions needing categorization"
        />
        <MetricCard
          label="Total Transactions"
          value={status?.counts.spending ?? 0}
        />
        <MetricCard
          label="Latest Spending"
          value={
            status?.latest_transactions.spending
              ? formatDate(status.latest_transactions.spending)
              : 'N/A'
          }
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Income Entries"
          value={status?.counts.income ?? 0}
        />
        <MetricCard
          label="Latest Income"
          value={
            status?.latest_transactions.income
              ? formatDate(status.latest_transactions.income)
              : 'N/A'
          }
        />
        <MetricCard
          label="Locations"
          value={status?.counts.locations ?? 0}
        />
        <MetricCard
          label="Data Source"
          value={status?.data_source ?? '-'}
        />
      </div>

      <div className="border-t pt-6">
        <h2 className="text-xl font-semibold mb-4">Hierarchy Tables</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard
            label="Categories"
            value={status?.counts.categories ?? 0}
            description="Top-level categories"
          />
          <MetricCard
            label="Sub Categories"
            value={status?.counts.sub_categories ?? 0}
            description="Middle-level categories"
          />
          <MetricCard
            label="Items"
            value={status?.counts.items ?? 0}
            description="Base-level items"
          />
        </div>
      </div>
    </div>
  )
}
