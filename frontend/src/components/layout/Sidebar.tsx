import { NavLink } from 'react-router-dom'
import {
  Home,
  TrendingDown,
  BarChart3,
  PlusCircle,
  MapPin,
  Layers,
  DollarSign,
  Bug,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/recent-spending', label: 'Recent Spending', icon: TrendingDown },
  { to: '/detailed-spending', label: 'Detailed Spending', icon: BarChart3 },
  { to: '/recording-expenses', label: 'Recording Expenses', icon: PlusCircle },
  { to: '/location-editing', label: 'Location Editing', icon: MapPin },
  { to: '/hierarchy-editing', label: 'Hierarchy Editing', icon: Layers },
  { to: '/income', label: 'Income', icon: DollarSign },
  { to: '/debug', label: 'Debug', icon: Bug },
]

export function Sidebar() {
  return (
    <aside className="w-64 border-r bg-muted/40 min-h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold">Expenses Dashboard</h1>
      </div>
      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
