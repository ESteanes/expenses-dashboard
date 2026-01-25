import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { fetchUncategorizedTransactions } from '@/api/transactions'
import { createSpendingEntry } from '@/api/spending'
import { formatCurrency, formatShortDate, getDateRange } from '@/lib/utils'
import type { Transaction } from '@/types'

export function RecordingExpensesPage() {
  const queryClient = useQueryClient()
  const defaultRange = getDateRange(30)
  const [startDate, setStartDate] = useState(defaultRange.start)
  const [endDate, setEndDate] = useState(defaultRange.end)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    item: '',
    cost: 0,
    quantity: 1,
    measure: '',
    location: '',
    shop: '',
    details: '',
    tag: '',
    date: '',
  })

  const { data: transactions, isLoading } = useQuery({
    queryKey: ['uncategorized-transactions', startDate, endDate],
    queryFn: () => fetchUncategorizedTransactions(startDate, endDate),
  })

  const createMutation = useMutation({
    mutationFn: createSpendingEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['uncategorized-transactions'] })
      queryClient.invalidateQueries({ queryKey: ['spending'] })
      setIsDialogOpen(false)
      setSelectedTransaction(null)
      resetForm()
    },
  })

  const resetForm = () => {
    setFormData({
      item: '',
      cost: 0,
      quantity: 1,
      measure: '',
      location: '',
      shop: '',
      details: '',
      tag: '',
      date: '',
    })
  }

  const handleTransactionSelect = (transaction: Transaction) => {
    setSelectedTransaction(transaction)
    setFormData({
      item: '',
      cost: Math.abs(transaction.Cost),
      quantity: 1,
      measure: '',
      location: '',
      shop: transaction.Shop || '',
      details: '',
      tag: '',
      date: transaction.Date.split('T')[0],
    })
    setIsDialogOpen(true)
  }

  const handleSubmit = () => {
    createMutation.mutate({
      Item: formData.item,
      Cost: formData.cost,
      Quantity: formData.quantity,
      Measure: formData.measure,
      Location: formData.location,
      Shop: formData.shop,
      Details: formData.details,
      Tag: formData.tag,
      Date: formData.date,
      transactionId: selectedTransaction?.transactionId,
    })
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
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => { resetForm(); setSelectedTransaction(null); }}>
              <Plus className="mr-2 h-4 w-4" />
              Add Expense
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>
                {selectedTransaction ? 'Categorize Transaction' : 'Add New Expense'}
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="item">Item</Label>
                <Input
                  id="item"
                  value={formData.item}
                  onChange={(e) => setFormData({ ...formData, item: e.target.value })}
                  placeholder="Enter item name"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cost">Cost</Label>
                  <Input
                    id="cost"
                    type="number"
                    step="0.01"
                    value={formData.cost}
                    onChange={(e) => setFormData({ ...formData, cost: parseFloat(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="shop">Shop</Label>
                  <Input
                    id="shop"
                    value={formData.shop}
                    onChange={(e) => setFormData({ ...formData, shop: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="tag">Tag</Label>
                <Input
                  id="tag"
                  value={formData.tag}
                  onChange={(e) => setFormData({ ...formData, tag: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input
                  id="date"
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="details">Details</Label>
                <Input
                  id="details"
                  value={formData.details}
                  onChange={(e) => setFormData({ ...formData, details: e.target.value })}
                />
              </div>
              <Button
                onClick={handleSubmit}
                disabled={!formData.item || createMutation.isPending}
                className="w-full"
              >
                {createMutation.isPending ? 'Saving...' : 'Save Expense'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
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
