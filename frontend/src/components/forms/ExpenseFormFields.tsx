import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { ExpenseFormData } from '@/hooks/useExpenseForm'

interface ExpenseFormFieldsProps {
  formData: ExpenseFormData
  onChange: <K extends keyof ExpenseFormData>(field: K, value: ExpenseFormData[K]) => void
}

export function ExpenseFormFields({ formData, onChange }: ExpenseFormFieldsProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="expense-item">Item</Label>
        <Input
          id="expense-item"
          value={formData.item}
          onChange={(e) => onChange('item', e.target.value)}
          placeholder="Enter item name"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="expense-cost">Cost</Label>
          <Input
            id="expense-cost"
            type="number"
            step="0.01"
            value={formData.cost}
            onChange={(e) => onChange('cost', parseFloat(e.target.value) || 0)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="expense-quantity">Quantity</Label>
          <Input
            id="expense-quantity"
            type="number"
            value={formData.quantity}
            onChange={(e) => onChange('quantity', parseFloat(e.target.value) || 1)}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="expense-shop">Shop</Label>
          <Input
            id="expense-shop"
            value={formData.shop}
            onChange={(e) => onChange('shop', e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="expense-location">Location</Label>
          <Input
            id="expense-location"
            value={formData.location}
            onChange={(e) => onChange('location', e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="expense-tag">Tag</Label>
        <Input
          id="expense-tag"
          value={formData.tag}
          onChange={(e) => onChange('tag', e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="expense-date">Date</Label>
        <Input
          id="expense-date"
          type="date"
          value={formData.date}
          onChange={(e) => onChange('date', e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="expense-details">Details</Label>
        <Input
          id="expense-details"
          value={formData.details}
          onChange={(e) => onChange('details', e.target.value)}
        />
      </div>
    </div>
  )
}
