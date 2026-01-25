import { cn } from '@/lib/utils'

interface Column {
  key: string
  label: string
  render?: (value: unknown, row: Record<string, unknown>) => React.ReactNode
  className?: string
}

interface DataTableProps {
  data: Record<string, unknown>[]
  columns: Column[]
  onRowClick?: (row: Record<string, unknown>, index: number) => void
  selectedIndex?: number
  className?: string
}

export function DataTable({
  data,
  columns,
  onRowClick,
  selectedIndex,
  className,
}: DataTableProps) {
  const getValue = (row: Record<string, unknown>, key: string): unknown => {
    const keys = key.split('.')
    let value: unknown = row
    for (const k of keys) {
      if (value && typeof value === 'object') {
        value = (value as Record<string, unknown>)[k]
      } else {
        value = undefined
      }
    }
    return value
  }

  return (
    <div className={cn('overflow-auto border rounded-lg', className)}>
      <table className="w-full text-sm">
        <thead className="bg-muted/50">
          <tr>
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className={cn(
                  'text-left p-3 font-medium text-muted-foreground',
                  col.className
                )}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr
              key={index}
              onClick={() => onRowClick?.(row, index)}
              className={cn(
                'border-t hover:bg-muted/50 transition-colors',
                onRowClick && 'cursor-pointer',
                selectedIndex === index && 'bg-primary/10'
              )}
            >
              {columns.map((col) => {
                const value = getValue(row, String(col.key))
                return (
                  <td key={String(col.key)} className={cn('p-3', col.className)}>
                    {col.render ? col.render(value, row) : String(value ?? '')}
                  </td>
                )
              })}
            </tr>
          ))}
          {data.length === 0 && (
            <tr>
              <td
                colSpan={columns.length}
                className="p-6 text-center text-muted-foreground"
              >
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
