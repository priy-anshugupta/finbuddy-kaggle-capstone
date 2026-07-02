'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    Wallet,
    TrendingUp,
    ArrowUpRight,
    ArrowDownRight,
    Activity,
    CreditCard,
    PieChart,
    Bell,
    Loader2,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { formatCurrency, formatDate } from '@/lib/utils'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { fetchDashboardSummary, fetchSpendingTrends, fetchAlerts } from '@/store/slices/dashboardSlice'
import { fetchTransactions } from '@/store/slices/transactionsSlice'
import { UntrackedCashWidget } from '@/components/common/UntrackedCashWidget'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement)

export default function DashboardPage() {
    const dispatch = useAppDispatch()
    const { summary, spendingTrends, alerts, isLoading: dashboardLoading } = useAppSelector((state: any) => state.dashboard)
    const { transactions, isLoading: transactionsLoading } = useAppSelector((state: any) => state.transactions)
    const { user } = useAppSelector((state: any) => state.auth)

    useEffect(() => {
        dispatch(fetchDashboardSummary())
        dispatch(fetchSpendingTrends('month'))
        dispatch(fetchAlerts())
        dispatch(fetchTransactions({ limit: 5 }))
    }, [dispatch])

    const isLoading = dashboardLoading || transactionsLoading

    // Calculate health score dynamically based on savings rate and financial metrics
    const savingsRate = summary?.savings_rate || 0
    
    // Improved health score calculation:
    // - Very negative (<-50%): 0-10 score (Critical)
    // - Negative (-50% to 0%): 10-30 score (Needs Work)
    // - 0-10% savings: 30-50 score (Fair)
    // - 10-20% savings: 50-70 score (Good)
    // - 20-30% savings: 70-85 score (Very Good)
    // - 30%+ savings: 85-100 score (Excellent)
    let healthScore = 0
    if (savingsRate < -50) {
        // Very negative: scale from 0-10
        healthScore = Math.max(0, Math.round(10 + (savingsRate + 50) * 0.2))
    } else if (savingsRate < 0) {
        // Negative savings rate: scale from 10-30 based on how negative
        healthScore = Math.round(30 + (savingsRate * 0.4)) // -50% = 10, 0% = 30
    } else if (savingsRate < 10) {
        // 0-10% savings: scale from 30-50
        healthScore = Math.round(30 + (savingsRate * 2))
    } else if (savingsRate < 20) {
        // 10-20% savings: scale from 50-70
        healthScore = Math.round(50 + ((savingsRate - 10) * 2))
    } else if (savingsRate < 30) {
        // 20-30% savings: scale from 70-85
        healthScore = Math.round(70 + ((savingsRate - 20) * 1.5))
    } else {
        // 30%+ savings: scale from 85-100
        healthScore = Math.min(100, Math.round(85 + ((savingsRate - 30) * 0.5)))
    }

    const getHealthLabel = (score: number) => {
        if (score >= 85) return { label: 'Excellent', color: 'text-green-400' }
        if (score >= 70) return { label: 'Very Good', color: 'text-green-400' }
        if (score >= 50) return { label: 'Good', color: 'text-blue-400' }
        if (score >= 30) return { label: 'Fair', color: 'text-yellow-400' }
        return { label: 'Needs Work', color: 'text-red-400' }
    }

    const healthInfo = getHealthLabel(healthScore)

    // Build chart data from spending trends - ensure it's always an array
    const trendsArray = Array.isArray(spendingTrends) ? spendingTrends : []
    const chartLabels = trendsArray.length > 0 
        ? trendsArray.map((t: any) => t.category || t.month || t.label)
        : (summary ? ['This Month'] : [])
    
    const spendingData = {
        labels: chartLabels.length > 0 ? chartLabels : ['No Data'],
        datasets: [
            {
                label: 'Income',
                data: trendsArray.length > 0 
                    ? trendsArray.map((t: any) => t.income || 0)
                    : (summary ? [summary.monthly_income] : [0]),
                borderColor: '#111111',
                backgroundColor: 'rgba(17, 17, 17, 0.1)',
                tension: 0.4,
            },
            {
                label: 'Expense',
                data: trendsArray.length > 0
                    ? trendsArray.map((t: any) => t.expenses || 0)
                    : (summary ? [summary.monthly_expenses] : [0]),
                borderColor: '#A3A3A3',
                backgroundColor: 'rgba(163, 163, 163, 0.1)',
                tension: 0.4,
            }
        ],
    }

    const chartOptions = {
        responsive: true,
        plugins: {
            legend: { position: 'top' as const, labels: { color: '#6B6B6B', font: { weight: 500 } } },
        },
        scales: {
            x: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { color: '#6B6B6B' } },
            y: { grid: { color: 'rgba(0, 0, 0, 0.05)' }, ticks: { color: '#6B6B6B' } },
        }
    }

    // Get category icon based on transaction category
    const getCategoryIcon = (category: string) => {
        return <CreditCard className="w-5 h-5 text-mono-500" />
    }

    return (
        <DashboardLayout>
            <div className="space-y-6">
                {/* Welcome Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-mono-900 tracking-tight">
                            Welcome back, <span className="text-mono-700">{user?.full_name || 'User'}</span> 👋
                        </h1>
                        <p className="text-mono-500 font-medium">Here's your financial health overview for today.</p>
                    </div>
                    <div className="flex items-center space-x-3">
                        {isLoading && (
                            <div className="flex items-center text-mono-500 text-sm font-medium">
                                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                Loading...
                            </div>
                        )}
                        <div className="glass-card px-4 py-2 flex items-center space-x-2">
                            <span className="w-2 h-2 rounded-full bg-mono-900 animate-pulse"></span>
                            <span className="text-xs text-mono-700 font-medium">Market Open</span>
                        </div>
                    </div>
                </div>

                {/* Bento Grid Layout */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">

                    {/* Financial Health Score - Onyx Card */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.1 }}
                        className="md:col-span-1 lg:row-span-2 onyx-card p-6 flex flex-col items-center justify-center"
                    >
                        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-widest mb-6">Financial Score</h3>
                        {isLoading && !summary ? (
                            <div className="relative w-40 h-40 flex items-center justify-center">
                                <Loader2 className="w-12 h-12 text-primary-500 animate-spin" />
                            </div>
                        ) : (
                            <>
                                <div className="relative w-40 h-40 flex items-center justify-center">
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle cx="80" cy="80" r="70" stroke="#1e293b" strokeWidth="10" fill="transparent" />
                                        <circle
                                            cx="80" cy="80" r="70" 
                                            stroke={healthScore >= 70 ? '#22c55e' : healthScore >= 50 ? '#3b82f6' : healthScore >= 30 ? '#eab308' : '#ef4444'}
                                            strokeWidth="10"
                                            fill="transparent"
                                            strokeDasharray="440"
                                            strokeDashoffset={440 - (440 * healthScore) / 100}
                                            className="transition-all duration-1000 ease-out"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                                        <span className="text-4xl font-bold text-white">{healthScore}</span>
                                        <span className={`text-xs font-medium pt-1 ${healthInfo.color}`}>{healthInfo.label}</span>
                                    </div>
                                </div>
                                <p className="text-xs text-center text-slate-500 mt-6 px-4">
                                    {summary ? (
                                        savingsRate >= 0 
                                            ? `Savings rate: +${savingsRate.toFixed(1)}%`
                                            : `Savings rate: ${savingsRate.toFixed(1)}%`
                                    ) : (
                                        'Add transactions to calculate your score'
                                    )}
                                </p>
                            </>
                        )}
                    </motion.div>

                    {/* Income vs Expenses Chart - Glass Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        className="md:col-span-2 lg:col-span-2 glass-card p-6"
                    >
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-bold text-mono-900 tracking-tight">Cash Flow</h3>
                            <span className="text-xs text-mono-500 font-medium">This Month</span>
                        </div>
                        <div className="h-48">
                            {summary ? (
                                <Line data={spendingData} options={{ ...chartOptions, maintainAspectRatio: false }} />
                            ) : (
                                <div className="h-full flex items-center justify-center text-mono-500 font-medium">
                                    No data yet - add transactions to see trends
                                </div>
                            )}
                        </div>
                    </motion.div>

                    {/* Quick Stats */}
                    <div className="md:col-span-3 lg:col-span-1 grid grid-cols-2 lg:grid-cols-1 gap-4">
                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 }}
                            className="glass-card p-4 flex flex-col justify-between h-full border-l-4 border-l-mono-900"
                        >
                            <div>
                                <p className="text-xs text-mono-500 uppercase font-semibold tracking-wide">Total Income</p>
                                <h4 className="text-xl font-bold text-mono-900 mt-1 tracking-tight">
                                    {formatCurrency(summary?.monthly_income || 0)}
                                </h4>
                            </div>
                            <div className="mt-2 text-xs text-mono-700 flex items-center font-medium">
                                <ArrowUpRight className="w-3 h-3 mr-1" /> This month
                            </div>
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 }}
                            className="glass-card p-4 flex flex-col justify-between h-full border-l-4 border-l-mono-400"
                        >
                            <div>
                                <p className="text-xs text-mono-500 uppercase font-semibold tracking-wide">Total Expenses</p>
                                <h4 className="text-xl font-bold text-mono-900 mt-1 tracking-tight">
                                    {formatCurrency(summary?.monthly_expenses || 0)}
                                </h4>
                            </div>
                            <div className="mt-2 text-xs text-mono-500 flex items-center font-medium">
                                <ArrowDownRight className="w-3 h-3 mr-1" /> This month
                            </div>
                        </motion.div>
                    </div>

                    {/* Recent Activity - Glass Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.5 }}
                        className="md:col-span-2 lg:col-span-2 glass-card p-6"
                    >
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-bold text-mono-900 tracking-tight">Recent Activity</h3>
                            <a href="/dashboard/transactions" className="text-xs text-mono-700 hover:text-mono-900 font-medium transition-all duration-300">View All</a>
                        </div>
                        <div className="space-y-1">
                            {transactions && transactions.length > 0 ? (
                                transactions.slice(0, 5).map((tx: any) => (
                                    <div key={tx.id} className="flex justify-between items-center p-3 hover:bg-mono-100/50 rounded-xl transition-all duration-300 cursor-pointer">
                                        <div className="flex items-center space-x-3 flex-1 min-w-0">
                                            <div className="w-10 h-10 rounded-xl bg-mono-100 flex items-center justify-center flex-shrink-0">
                                                {getCategoryIcon(tx.category)}
                                            </div>
                                            <div className="min-w-0">
                                                <p className="text-sm font-medium text-mono-900 truncate">{tx.merchant || tx.description || 'Transaction'}</p>
                                                <p className="text-xs text-mono-500">{tx.category} • {formatDate(tx.date || tx.transaction_date)}</p>
                                            </div>
                                        </div>
                                        <span className={`text-sm font-bold flex-shrink-0 ml-3 ${tx.type === 'credit' ? 'text-green-600' : 'text-mono-600'}`}>
                                            {tx.type === 'credit' ? '+' : '-'}{formatCurrency(tx.amount)}
                                        </span>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-8 text-mono-500">
                                    <CreditCard className="w-12 h-12 mx-auto mb-3 opacity-30" />
                                    <p className="font-medium">No transactions yet</p>
                                    <a href="/dashboard/transactions" className="text-mono-700 text-sm hover:underline font-medium">Add your first transaction</a>
                                </div>
                            )}
                        </div>
                    </motion.div>

                    {/* Untracked Cash Widget */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.55 }}
                        className="md:col-span-1 lg:col-span-2"
                    >
                        <UntrackedCashWidget />
                    </motion.div>

                    {/* Smart Alerts - Onyx Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 }}
                        className="md:col-span-1 lg:col-span-2 onyx-card p-6 relative overflow-hidden"
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-5">
                            <Bell className="w-32 h-32 text-white" />
                        </div>
                        <h3 className="text-lg font-bold text-white mb-4 relative z-10 tracking-tight">Smart Alerts</h3>
                        <div className="space-y-3 relative z-10">
                            {alerts && alerts.length > 0 ? (
                                alerts.slice(0, 3).map((alert: any) => (
                                    <div
                                        key={alert.id}
                                        className="p-3 rounded-xl flex items-start space-x-3 bg-white/5 border border-white/10"
                                    >
                                        <Activity className="w-5 h-5 mt-0.5 text-white/70" />
                                        <div>
                                            <p className="text-sm font-medium text-white">{alert.title}</p>
                                            <p className="text-xs text-white/50">{alert.message}</p>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="p-3 bg-white/5 border border-white/10 rounded-xl flex items-start space-x-3">
                                    <TrendingUp className="w-5 h-5 text-white/70 mt-0.5" />
                                    <div>
                                        <p className="text-sm font-medium text-white">All Clear!</p>
                                        <p className="text-xs text-white/50">No alerts at this time. Your finances look healthy.</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    </motion.div>

                </div>
            </div>
        </DashboardLayout>
    )
}
