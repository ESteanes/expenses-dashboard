import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { LoadingPage } from '@/components/common/LoadingSpinner'
import { MetricCard } from '@/components/common/MetricCard'
import { DateRangePicker } from '@/components/common/DateRangePicker'
import { DataTable } from '@/components/common/DataTable'
import { BarChart } from '@/components/charts/BarChart'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  fetchIncome,
  fetchIncomeSummary,
  fetchIncomeFilterOptions,
  createIncomeEntry,
  deleteIncomeEntry,
} from '@/api/income'
import { formatCurrency, formatShortDate, getDateRange } from '@/lib/utils'

export function IncomePage() {
  const queryClient = useQueryClient()
  const defaultRange = getDateRange(365)
  const [startDate, setStartDate] = useState(defaultRange.start)
  const [endDate, setEndDate] = useState(defaultRange.end)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    gross_income: 0,
    salary_sacrifice: 0,
    tax: 0,
    income: 0,
    date: '',
    employer: '',
    description: '',
    taxable: 'Taxable' as 'Taxable' | 'Not-taxable' | 'Franked Dividends',
    comment: '',
  })

  const { data: income, isLoading: incomeLoading } = useQuery({
    queryKey: ['income', startDate, endDate],
    queryFn: () => fetchIncome({ start_date: startDate, end_date: endDate }),
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['income-summary', startDate, endDate],
    queryFn: () => fetchIncomeSummary(startDate, endDate),
  })

  // Filter options for future use
  useQuery({
    queryKey: ['income-filters'],
    queryFn: fetchIncomeFilterOptions,
  })

  const createMutation = useMutation({
    mutationFn: createIncomeEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['income'] })
      queryClient.invalidateQueries({ queryKey: ['income-summary'] })
      setIsDialogOpen(false)
      resetForm()
    },
  })

  // Delete mutation for future use
  useMutation({
    mutationFn: deleteIncomeEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['income'] })
      queryClient.invalidateQueries({ queryKey: ['income-summary'] })
    },
  })

  const resetForm = () => {
    setFormData({
      gross_income: 0,
      salary_sacrifice: 0,
      tax: 0,
      income: 0,
      date: '',
      employer: '',
      description: '',
      taxable: 'Taxable',
      comment: '',
    })
  }

  const handleSubmit = () => {
    createMutation.mutate({
      'Gross Income': formData.gross_income,
      'Salary Sacrifice': formData.salary_sacrifice,
      Tax: formData.tax,
      Income: formData.income,
      Date: formData.date,
      Employer: formData.employer,
      Description: formData.description,
      Taxable: formData.taxable,
      Comment: formData.comment,
      'Received in bank account': 'Yes',
    })
  }

  if (incomeLoading || summaryLoading) return <LoadingPage />

  // Prepare chart data
  const byEmployer = summary?.by_employer
    ? Object.entries(summary.by_employer).map(([name, data]) => ({
        name,
        value: data['Gross Income'],
      }))
    : []

  const byFinancialYear = summary?.by_financial_year
    ? Object.entries(summary.by_financial_year).map(([name, data]) => ({
        name,
        value: data['Gross Income'],
      }))
    : []

  const columns = [
    { key: 'Date', label: 'Date', render: (v: unknown) => formatShortDate(String(v)) },
    { key: 'Employer', label: 'Employer' },
    { key: 'Description', label: 'Description' },
    { key: 'Gross Income', label: 'Gross', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'Tax', label: 'Tax', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'Income', label: 'Net', render: (v: unknown) => formatCurrency(Number(v)) },
    { key: 'Financial Year', label: 'FY' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Income</h1>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Income
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Add Income Entry</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Gross Income</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.gross_income}
                    onChange={(e) =>
                      setFormData({ ...formData, gross_income: parseFloat(e.target.value) })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label>Tax</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.tax}
                    onChange={(e) =>
                      setFormData({ ...formData, tax: parseFloat(e.target.value) })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Salary Sacrifice</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.salary_sacrifice}
                    onChange={(e) =>
                      setFormData({ ...formData, salary_sacrifice: parseFloat(e.target.value) })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label>Net Income</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={formData.income}
                    onChange={(e) =>
                      setFormData({ ...formData, income: parseFloat(e.target.value) })
                    }
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Date</Label>
                <Input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Employer</Label>
                <Input
                  value={formData.employer}
                  onChange={(e) => setFormData({ ...formData, employer: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Input
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Taxable</Label>
                <Select
                  value={formData.taxable}
                  onValueChange={(v) =>
                    setFormData({ ...formData, taxable: v as typeof formData.taxable })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Taxable">Taxable</SelectItem>
                    <SelectItem value="Not-taxable">Not-taxable</SelectItem>
                    <SelectItem value="Franked Dividends">Franked Dividends</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={handleSubmit}
                disabled={!formData.employer || !formData.date || createMutation.isPending}
                className="w-full"
              >
                {createMutation.isPending ? 'Saving...' : 'Save Income'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Gross Income"
          value={formatCurrency(summary?.total_gross ?? 0)}
          className="bg-green-50"
        />
        <MetricCard
          label="Total Tax"
          value={formatCurrency(summary?.total_tax ?? 0)}
          className="bg-red-50"
        />
        <MetricCard
          label="Total Net Income"
          value={formatCurrency(summary?.total_net ?? 0)}
          className="bg-blue-50"
        />
        <MetricCard
          label="Entries"
          value={income?.length ?? 0}
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
        </div>

        {/* Main content */}
        <div className="flex-1 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="border rounded-lg p-4">
              <BarChart
                data={byEmployer}
                title="Income by Employer"
                color="#10b981"
              />
            </div>
            <div className="border rounded-lg p-4">
              <BarChart
                data={byFinancialYear}
                title="Income by Financial Year"
                color="#3b82f6"
              />
            </div>
          </div>

          <div className="border rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-4">Income Entries</h3>
            <DataTable
              data={(income ?? []) as unknown as Record<string, unknown>[]}
              columns={columns}
              className="max-h-96"
            />
          </div>
        </div>
      </div>
    </div>
  )
}
