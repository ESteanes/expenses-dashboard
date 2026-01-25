import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchTransactions, fetchRawTransactions } from '@/api/transactions'
import { formatCurrency, formatShortDate, getDateRange } from '@/lib/utils'

export function DebugPage() {
  const defaultRange = getDateRange(30)
  const [startDate, setStartDate] = useState(defaultRange.start)
  const [endDate, setEndDate] = useState(defaultRange.end)

  const { data: transactions, isLoading: transactionsLoading } = useQuery({
    queryKey: ['transactions', startDate, endDate],
    queryFn: () => fetchTransactions(startDate, endDate),
  })

  const { data: rawTransactions, isLoading: rawLoading } = useQuery({
    queryKey: ['raw-transactions', startDate, endDate],
    queryFn: () => fetchRawTransactions(startDate, endDate),
  })

  if (transactionsLoading || rawLoading) return <LoadingPage />

  const transactionColumns = [
    { key: 'Date', label: 'Date', render: (v: unknown) => formatShortDate(String(v)) },
    { key: 'Shop', label: 'Shop' },
    { key: 'Cost', label: 'Cost', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'transactionId', label: 'Transaction ID' },
    { key: 'Upbank Category', label: 'Bank Category' },
  ]

  const rawColumns = [
    { key: 'createdAt', label: 'Date' },
    { key: 'description', label: 'Description' },
    { key: 'Cost', label: 'Amount', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'Category', label: 'Category' },
    { key: 'transactionId', label: 'ID' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Debug</h1>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 space-y-6 shrink-0">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
          <div className="text-sm text-muted-foreground space-y-1">
            <p>Processed: {transactions?.length ?? 0} transactions</p>
            <p>Raw: {rawTransactions?.length ?? 0} transactions</p>
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Processed Transactions (CSV Endpoint)</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable
                data={(transactions ?? []) as unknown as Record<string, unknown>[]}
                columns={transactionColumns}
                className="max-h-80"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Raw Transactions (API Response)</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable
                data={(rawTransactions ?? []) as unknown as Record<string, unknown>[]}
                columns={rawColumns}
                className="max-h-80"
              />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
