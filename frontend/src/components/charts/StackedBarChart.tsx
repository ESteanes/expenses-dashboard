import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface StackedBarChartProps {
  data: Record<string, unknown>[]
  categories: string[]
  xKey: string
  title: string
  height?: number
  colors?: string[]
}

const DEFAULT_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
  '#84cc16', // lime
]

export function StackedBarChart({
  data,
  categories,
  xKey,
  title,
  height = 300,
  colors = DEFAULT_COLORS,
}: StackedBarChartProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data}>
          <XAxis
            dataKey={xKey}
            tick={{ fontSize: 12 }}
            angle={-30}
            textAnchor="end"
            height={60}
          />
          <YAxis
            tickFormatter={(value) => formatCurrency(value)}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Legend />
          {categories.map((category, index) => (
            <Bar
              key={category}
              dataKey={category}
              stackId="stack"
              fill={colors[index % colors.length]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
