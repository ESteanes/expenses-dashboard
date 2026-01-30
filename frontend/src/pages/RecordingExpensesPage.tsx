import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { AddExpenseDialog } from '@/components/forms/AddExpenseDialog'
import { fetchUncategorizedTransactions } from '@/api/transactions'
import { formatCurrency, formatShortDate, getDateRange } from '@/lib/utils'
import type { Transaction } from '@/types'

export function RecordingExpensesPage() {
  const defaultRange = getDateRange(30)
  const [startDate, setStartDate] = useState(defaultRange.start)
  const [endDate, setEndDate] = useState(defaultRange.end)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const { data: transactions, isLoading } = useQuery({
    queryKey: ['uncategorized-transactions', startDate, endDate],
    queryFn: () => fetchUncategorizedTransactions(startDate, endDate),
  })

  const handleTransactionSelect = (transaction: Transaction) => {
    setSelectedTransaction(transaction)
    setIsDialogOpen(true)
  }

  const handleDialogClose = (open: boolean) => {
    setIsDialogOpen(open)
    if (!open) {
      setSelectedTransaction(null)
    }
  }

  if (isLoading) return <LoadingPage />

  const columns = [
    { key: 'Date', label: 'Date', render: (v: unknown) => formatShortDate(String(v)) },
    { key: 'Shop', label: 'Shop' },
    { key: 'Cost', label: 'Cost', render: (v: unknown) => formatCurrency(Math.abs(Number(v))) },
    { key: 'Upbank Category', label: 'Bank Category' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Recording Expenses</h1>

        {/* Dialog for adding new expense (no transaction) */}
        <AddExpenseDialog />

        {/* Dialog for categorizing selected transaction */}
        {/* Dialog for categorizing selected transaction - hidden trigger, opened programmatically */}
        <AddExpenseDialog
          open={isDialogOpen}
          onOpenChange={handleDialogClose}
          title="Categorize Transaction"
          trigger={<span />}
          transactionId={selectedTransaction?.transactionId}
          defaultValues={
            selectedTransaction
              ? {
                  cost: Math.abs(selectedTransaction.Cost),
                  shop: selectedTransaction.Shop || '',
                  date: selectedTransaction.Date.split('T')[0],
                }
              : undefined
          }
        />
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 space-y-6 shrink-0">
          <DateRangePicker
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
          <div className="text-sm text-muted-foreground">
            {transactions?.length ?? 0} uncategorized transactions
          </div>
        </div>

        {/* Main content */}
        <div className="flex-1">
          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Uncategorized Transactions</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Click a transaction to categorize it
            </p>
            <DataTable
              data={(transactions ?? []) as unknown as Record<string, unknown>[]}
              columns={columns}
              onRowClick={(row) => handleTransactionSelect(row as unknown as Transaction)}
              className="max-h-[600px]"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
