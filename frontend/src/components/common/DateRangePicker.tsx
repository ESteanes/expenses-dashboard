import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface DateRangePickerProps {
  startDate: string
  endDate: string
  onStartDateChange: (date: string) => void
  onEndDateChange: (date: string) => void
}

export function DateRangePicker({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}: DateRangePickerProps) {
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="start-date">Start Date</Label>
        <Input
          id="start-date"
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="end-date">End Date</Label>
        <Input
          id="end-date"
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
        />
      </div>
    </div>
  )
}
