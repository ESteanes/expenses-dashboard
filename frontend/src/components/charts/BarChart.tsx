import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface BarChartProps {
  data: { name: string; value: number }[]
  title: string
  maxItems?: number
  color?: string
  height?: number
}

export function BarChart({
  data,
  title,
  maxItems = 20,
  color = '#3b82f6',
  height = 300,
}: BarChartProps) {
  // Sort by value descending and limit
  const chartData = [...data]
    .sort((a, b) => b.value - a.value)
    .slice(0, maxItems)

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart data={chartData} layout="horizontal">
          <XAxis
            dataKey="name"
            angle={-30}
            textAnchor="end"
            height={80}
            tick={{ fontSize: 12 }}
            interval={0}
          />
          <YAxis
            tickFormatter={(value) => formatCurrency(value)}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Cost']}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Bar dataKey="value" fill={color}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={color} opacity={0.8} />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}

interface HorizontalBarChartProps {
  data: { name: string; value: number }[]
  title: string
  maxItems?: number
  color?: string
  height?: number
}

export function HorizontalBarChart({
  data,
  title,
  maxItems = 10,
  color = '#3b82f6',
  height = 400,
}: HorizontalBarChartProps) {
  // Sort by value descending and limit
  const chartData = [...data]
    .sort((a, b) => b.value - a.value)
    .slice(0, maxItems)

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsBarChart data={chartData} layout="vertical">
          <XAxis
            type="number"
            tickFormatter={(value) => formatCurrency(value)}
            tick={{ fontSize: 12 }}
          />
          <YAxis
            dataKey="name"
            type="category"
            width={120}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => [formatCurrency(value), 'Cost']}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Bar dataKey="value" fill={color}>
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={color} opacity={0.8} />
            ))}
          </Bar>
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}
