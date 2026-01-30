import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createSpendingEntry } from '@/api/spending'

export interface ExpenseFormData {
  item: string
  cost: number
  quantity: number
  measure: string
  location: string
  shop: string
  details: string
  tag: string
  date: string
}

const DEFAULT_FORM_DATA: ExpenseFormData = {
  item: '',
  cost: 0,
  quantity: 1,
  measure: '',
  location: '',
  shop: '',
  details: '',
  tag: '',
  date: '',
}

interface UseExpenseFormOptions {
  onSuccess?: () => void
  transactionId?: string
}

export function useExpenseForm(options: UseExpenseFormOptions = {}) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<ExpenseFormData>(DEFAULT_FORM_DATA)

  const mutation = useMutation({
    mutationFn: createSpendingEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['uncategorized-transactions'] })
      queryClient.invalidateQueries({ queryKey: ['spending'] })
      queryClient.invalidateQueries({ queryKey: ['recent-spending'] })
      queryClient.invalidateQueries({ queryKey: ['system-status'] })
      resetForm()
      options.onSuccess?.()
    },
  })

  const resetForm = () => {
    setFormData(DEFAULT_FORM_DATA)
  }

  const setField = <K extends keyof ExpenseFormData>(
    field: K,
    value: ExpenseFormData[K]
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
  }

  const setFromTransaction = (transaction: {
    Cost: number
    Shop?: string
    Date: string
  }) => {
    setFormData({
      ...DEFAULT_FORM_DATA,
      cost: Math.abs(transaction.Cost),
      shop: transaction.Shop || '',
      date: transaction.Date.split('T')[0],
    })
  }

  const submit = (transactionId?: string) => {
    mutation.mutate({
      Item: formData.item,
      Cost: formData.cost,
      Quantity: formData.quantity,
      Measure: formData.measure,
      Location: formData.location,
      Shop: formData.shop,
      Details: formData.details,
      Tag: formData.tag,
      Date: formData.date,
      transactionId: transactionId || options.transactionId,
    })
  }

  const isValid = formData.item.trim() !== ''

  return {
    formData,
    setFormData,
    setField,
    setFromTransaction,
    resetForm,
    submit,
    isValid,
    isPending: mutation.isPending,
    isError: mutation.isError,
    error: mutation.error,
  }
}
