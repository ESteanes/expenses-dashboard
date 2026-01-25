import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface PieChartProps {
  data: { name: string; value: number }[]
  title: string
  height?: number
  colors?: string[]
}

const DEFAULT_COLORS = [
  '#3b82f6',
  '#ef4444',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#84cc16',
]

export function PieChart({
  data,
  title,
  height = 300,
  colors = DEFAULT_COLORS,
}: PieChartProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsPieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={80}
            label={({ name, percent }) =>
              `${name}: ${(percent * 100).toFixed(0)}%`
            }
            labelLine={false}
          >
            {data.map((_, index) => (
              <Cell
                key={`cell-${index}`}
                fill={colors[index % colors.length]}
              />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => formatCurrency(value)} />
          <Legend />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  )
}
