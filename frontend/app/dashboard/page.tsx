'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { DollarSign, TrendingUp, TrendingDown, Upload, ArrowRight } from 'lucide-react'
import { api } from '@/lib/api'
import { supabase } from '@/lib/supabase'
import { StatsCard } from '@/components/dashboard/StatsCard'

interface Transaction {
  id: string
  date: string
  amount: number
  description: string | null
  merchant: string | null
  status: string
}

interface Summary {
  total_transactions: number
  total_income: number
  total_expenses: number
  net_amount: number
  pending_review: number
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function DashboardPage() {
  const [userEmail, setUserEmail] = useState<string>('')
  const [summary, setSummary] = useState<Summary | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        if (session?.user.email) {
          setUserEmail(session.user.email)
        }

        const [summaryRes, transactionsRes] = await Promise.all([
          api.transactions.summary(),
          api.transactions.list({ limit: 5 }),
        ])

        setSummary(summaryRes.data)
        setTransactions(transactionsRes.data)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 w-64 rounded" style={{ backgroundColor: 'var(--bg-secondary)' }} />
          <div className="grid grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 rounded-lg" style={{ backgroundColor: 'var(--bg-secondary)' }} />
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-semibold" style={{ color: 'var(--text-primary)' }}>
            Welcome back
          </h1>
          <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
            {userEmail}
          </p>
        </div>
        <Link
          href="/dashboard/documents"
          className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-colors"
          style={{
            backgroundColor: 'var(--accent)',
            color: 'white',
          }}
        >
          <Upload size={18} />
          Upload Document
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <StatsCard
          title="Total Income"
          value={formatCurrency(summary?.total_income || 0)}
          icon={TrendingUp}
          variant="success"
        />
        <StatsCard
          title="Total Expenses"
          value={formatCurrency(summary?.total_expenses || 0)}
          icon={TrendingDown}
          variant="danger"
        />
        <StatsCard
          title="Net Amount"
          value={formatCurrency(summary?.net_amount || 0)}
          icon={DollarSign}
          variant={(summary?.net_amount || 0) >= 0 ? 'success' : 'danger'}
        />
      </div>

      {/* Recent Transactions */}
      <div
        className="rounded-lg border"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="p-6 border-b" style={{ borderColor: 'var(--border)' }}>
          <h2 className="text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
            Recent Transactions
          </h2>
        </div>

        {transactions.length === 0 ? (
          <div className="p-12 text-center">
            <p style={{ color: 'var(--text-secondary)' }}>
              No transactions yet. Upload a document to get started.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th
                    className="text-left text-xs font-medium uppercase tracking-wider px-6 py-3"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Date
                  </th>
                  <th
                    className="text-left text-xs font-medium uppercase tracking-wider px-6 py-3"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Merchant
                  </th>
                  <th
                    className="text-left text-xs font-medium uppercase tracking-wider px-6 py-3"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Description
                  </th>
                  <th
                    className="text-right text-xs font-medium uppercase tracking-wider px-6 py-3"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr
                    key={transaction.id}
                    className="transition-colors hover:bg-[var(--bg-tertiary)]"
                    style={{ borderBottom: '1px solid var(--border)' }}
                  >
                    <td className="px-6 py-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {format(new Date(transaction.date), 'MMM d, yyyy')}
                    </td>
                    <td className="px-6 py-4 text-sm" style={{ color: 'var(--text-primary)' }}>
                      {transaction.merchant || '—'}
                    </td>
                    <td className="px-6 py-4 text-sm" style={{ color: 'var(--text-secondary)' }}>
                      {transaction.description || '—'}
                    </td>
                    <td
                      className="px-6 py-4 text-sm text-right font-medium"
                      style={{
                        color: transaction.amount >= 0 ? 'var(--success)' : 'var(--danger)',
                      }}
                    >
                      {transaction.amount >= 0 ? '+' : ''}
                      {formatCurrency(transaction.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {transactions.length > 0 && (
          <div className="p-4 border-t" style={{ borderColor: 'var(--border)' }}>
            <Link
              href="/dashboard/transactions"
              className="flex items-center justify-center gap-2 text-sm font-medium transition-colors"
              style={{ color: 'var(--accent)' }}
            >
              View all transactions
              <ArrowRight size={16} />
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
