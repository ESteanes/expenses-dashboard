import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { formatCurrency } from '@/lib/utils'

interface LineChartProps {
  data: Record<string, unknown>[]
  lines: { key: string; color: string; name?: string }[]
  xKey: string
  title: string
  height?: number
}

export function LineChart({
  data,
  lines,
  xKey,
  title,
  height = 300,
}: LineChartProps) {
  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <RechartsLineChart data={data}>
          <XAxis dataKey={xKey} tick={{ fontSize: 12 }} />
          <YAxis
            tickFormatter={(value) => formatCurrency(value)}
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            labelStyle={{ fontWeight: 'bold' }}
          />
          <Legend />
          {lines.map((line) => (
            <Line
              key={line.key}
              type="monotone"
              dataKey={line.key}
              name={line.name || line.key}
              stroke={line.color}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </RechartsLineChart>
      </ResponsiveContainer>
    </div>
  )
}
