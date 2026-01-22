import { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: string
  icon: LucideIcon
  trend?: {
    value: number
    isPositive: boolean
  }
  variant?: 'default' | 'success' | 'danger'
}

export function StatsCard({ title, value, icon: Icon, trend, variant = 'default' }: StatsCardProps) {
  const getValueColor = () => {
    switch (variant) {
      case 'success':
        return 'var(--success)'
      case 'danger':
        return 'var(--danger)'
      default:
        return 'var(--text-primary)'
    }
  }

  return (
    <div
      className="p-6 rounded-lg border"
      style={{
        backgroundColor: 'var(--bg-secondary)',
        borderColor: 'var(--border)',
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-medium" style={{ color: 'var(--text-secondary)' }}>
          {title}
        </span>
        <Icon size={20} style={{ color: 'var(--text-muted)' }} />
      </div>
      <div className="flex items-end gap-2">
        <span
          className="text-2xl font-semibold"
          style={{ color: getValueColor() }}
        >
          {value}
        </span>
        {trend && (
          <span
            className="text-sm mb-0.5"
            style={{
              color: trend.isPositive ? 'var(--success)' : 'var(--danger)',
            }}
          >
            {trend.isPositive ? '+' : ''}{trend.value}%
          </span>
        )}
      </div>
    </div>
  )
}
