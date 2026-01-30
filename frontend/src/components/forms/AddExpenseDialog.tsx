import { useState, useEffect, ReactNode } from 'react'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { ExpenseFormFields } from './ExpenseFormFields'
import { useExpenseForm } from '@/hooks/useExpenseForm'

interface DefaultValues {
  cost?: number
  shop?: string
  date?: string
}

interface AddExpenseDialogProps {
  /** Optional custom trigger button. If not provided, uses default "Add Expense" button */
  trigger?: ReactNode
  /** Title for the dialog */
  title?: string
  /** Default values to pre-fill the form */
  defaultValues?: DefaultValues
  /** Transaction ID to link with (for categorizing bank transactions) */
  transactionId?: string
  /** Controlled open state */
  open?: boolean
  /** Callback when open state changes */
  onOpenChange?: (open: boolean) => void
  /** Variant for the default trigger button */
  triggerVariant?: 'default' | 'outline' | 'ghost' | 'secondary'
  /** Size for the default trigger button */
  triggerSize?: 'default' | 'sm' | 'lg' | 'icon'
  /** Whether to show icon in default trigger */
  showIcon?: boolean
  /** Custom label for default trigger */
  triggerLabel?: string
}

export function AddExpenseDialog({
  trigger,
  title = 'Add New Expense',
  defaultValues,
  transactionId,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
  triggerVariant = 'default',
  triggerSize = 'default',
  showIcon = true,
  triggerLabel = 'Add Expense',
}: AddExpenseDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)

  // Support both controlled and uncontrolled modes
  const isControlled = controlledOpen !== undefined
  const open = isControlled ? controlledOpen : internalOpen
  const setOpen = isControlled ? controlledOnOpenChange! : setInternalOpen

  const { formData, setField, resetForm, submit, isValid, isPending } = useExpenseForm({
    onSuccess: () => {
      setOpen(false)
    },
  })

  // Apply default values when dialog opens or defaultValues change
  useEffect(() => {
    if (open && defaultValues) {
      if (defaultValues.cost !== undefined) setField('cost', defaultValues.cost)
      if (defaultValues.shop) setField('shop', defaultValues.shop)
      if (defaultValues.date) setField('date', defaultValues.date)
    }
  }, [open, defaultValues])

  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen) {
      resetForm()
    }
    setOpen(newOpen)
  }

  const handleSubmit = () => {
    submit(transactionId)
  }

  const defaultTrigger = (
    <Button variant={triggerVariant} size={triggerSize}>
      {showIcon && <Plus className="mr-2 h-4 w-4" />}
      {triggerLabel}
    </Button>
  )

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        {trigger || defaultTrigger}
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <ExpenseFormFields formData={formData} onChange={setField} />
        <Button
          onClick={handleSubmit}
          disabled={!isValid || isPending}
          className="w-full"
        >
          {isPending ? 'Saving...' : 'Save Expense'}
        </Button>
      </DialogContent>
    </Dialog>
  )
}
