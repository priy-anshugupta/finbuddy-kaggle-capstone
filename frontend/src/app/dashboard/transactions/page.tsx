'use client'

import { useState, useEffect, useMemo } from 'react'
import { motion } from 'framer-motion'
import {
    Wallet,
    ArrowUpRight,
    ArrowDownRight,
    Search,
    Filter,
    RefreshCcw,
    Download,
    Calendar,
    CreditCard,
    ShoppingBag,
    Coffee,
    Zap,
    Loader2,
    Banknote,
    TrendingDown,
    EyeOff,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { formatCurrency, formatDate, getCategoryColor, getCategoryIcon } from '@/lib/utils'
import { useAppDispatch, useAppSelector, RootState } from '@/store/hooks'
import { fetchTransactions, fetchTransactionStats } from '@/store/slices/transactionsSlice'
import { AddTransactionModal } from '@/components/common/AddTransactionModal'
import { UntrackedCashWidget } from '@/components/common/UntrackedCashWidget'

// Loading skeleton component for fast perceived loading
function TransactionSkeleton() {
    return (
        <div className="animate-pulse">
            {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center px-6 py-4 border-b border-gray-200">
                    <div className="w-8 h-8 rounded-lg bg-gray-200 mr-3" />
                    <div className="flex-1">
                        <div className="h-4 bg-gray-200 rounded w-32 mb-2" />
                        <div className="h-3 bg-gray-100 rounded w-20" />
                    </div>
                    <div className="h-4 bg-gray-200 rounded w-20" />
                </div>
            ))}
        </div>
    )
}

// Stats skeleton for loading state
function StatsSkeleton() {
    return (
        <div className="glass-card p-6 animate-pulse">
            <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-gray-200" />
                <div className="h-4 bg-gray-200 rounded w-16" />
            </div>
            <div className="h-3 bg-gray-100 rounded w-24 mb-2" />
            <div className="h-6 bg-gray-200 rounded w-32" />
        </div>
    )
}

export default function TransactionsPage() {
    const dispatch = useAppDispatch()
    const { transactions, stats, isLoading } = useAppSelector((state: any) => state.transactions)
    const [searchTerm, setSearchTerm] = useState('')
    const [selectedCategory, setSelectedCategory] = useState('All')
    const [isInitialLoad, setIsInitialLoad] = useState(true)
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [widgetKey, setWidgetKey] = useState(0)
    const [cashData, setCashData] = useState<any>(null)
    const [isCashLoading, setIsCashLoading] = useState(true)

    // Fetch cash check data
    const fetchCashData = async () => {
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cash-check/summary`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            if (response.ok) {
                const data = await response.json()
                setCashData(data)
            }
        } catch (error) {
            console.error('Error fetching cash data:', error)
        } finally {
            setIsCashLoading(false)
        }
    }

    // Hide (delete) transaction
    const handleHideTransaction = async (transactionId: string) => {
        if (!confirm('Are you sure you want to hide this transaction? This action cannot be undone.')) {
            return
        }

        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/transactions/${transactionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })

            if (response.ok) {
                // Refresh transactions and stats
                dispatch(fetchTransactions({}))
                dispatch(fetchTransactionStats('month'))
                fetchCashData()
                setWidgetKey(prev => prev + 1)
            } else {
                console.error('Failed to hide transaction')
            }
        } catch (error) {
            console.error('Error hiding transaction:', error)
        }
    }

    useEffect(() => {
        // Fetch both in parallel for faster loading
        const loadData = async () => {
            await Promise.all([
                dispatch(fetchTransactions({})),
                dispatch(fetchTransactionStats('month')),
                fetchCashData()
            ])
            setIsInitialLoad(false)
        }
        
        // Only fetch if we don't have data already (prevents re-fetch on tab switch)
        if (transactions.length === 0 || !stats) {
            loadData()
        } else {
            setIsInitialLoad(false)
            if (!cashData) fetchCashData()
        }
    }, [dispatch])

    // Memoize filtered results to avoid recalculation on every render
    const recurringPayments = useMemo(() => 
        transactions.filter((t: any) => t.is_recurring), 
        [transactions]
    )

    const filteredTransactions = useMemo(() => 
        transactions.filter((t: any) =>
            (selectedCategory === 'All' || (t.category || '').toLowerCase() === selectedCategory.toLowerCase()) &&
            ((t.merchant_name || t.merchant || t.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                (t.category || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                (t.subcategory || '').toLowerCase().includes(searchTerm.toLowerCase()))
        ),
        [transactions, selectedCategory, searchTerm]
    )

    return (
        <DashboardLayout>
            <div className="space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
                        <p className="text-gray-500">Manage and track your financial activity</p>
                    </div>
                    <div className="flex items-center space-x-3">
                        <button className="btn-secondary flex items-center space-x-2">
                            <Download className="w-4 h-4" />
                            <span>Export</span>
                        </button>
                        <button 
                            onClick={() => setIsModalOpen(true)}
                            className="btn-primary flex items-center space-x-2"
                        >
                            <Wallet className="w-4 h-4" />
                            <span>Add New</span>
                        </button>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {isInitialLoad && !stats ? (
                        <>
                            <StatsSkeleton />
                            <StatsSkeleton />
                            <StatsSkeleton />
                        </>
                    ) : (
                        <>
                            <motion.div
                                className="glass-card p-6"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                                        <ArrowUpRight className="w-6 h-6 text-white" />
                                    </div>
                                    <span className="text-green-400 text-sm font-medium">This month</span>
                                </div>
                                <p className="text-sm text-gray-500">Total Income</p>
                                <p className="text-2xl font-bold text-gray-900 mt-1">
                                    {formatCurrency(stats?.total_income || 0)}
                                </p>
                            </motion.div>

                            <motion.div
                                className="glass-card p-6"
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.2 }}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-600 flex items-center justify-center">
                                <ArrowDownRight className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-red-400 text-sm font-medium">This month</span>
                        </div>
                        <p className="text-sm text-gray-500">Total Expenses</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">
                            {formatCurrency(stats?.total_expenses || 0)}
                        </p>
                    </motion.div>

                    <motion.div
                        className="glass-card p-6"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                                <Wallet className="w-6 h-6 text-white" />
                            </div>
                            <span className={`text-sm font-medium ${
                                (stats?.net_savings || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                            }`}>
                                {(stats?.net_savings || 0) >= 0 ? 'Healthy' : 'Review'}
                            </span>
                        </div>
                        <p className="text-sm text-gray-500">Net Savings</p>
                        <p className={`text-2xl font-bold mt-1 ${
                            (stats?.net_savings || 0) >= 0 ? 'text-gray-900' : 'text-red-500'
                        }`}>
                            {formatCurrency(stats?.net_savings || 0)}
                        </p>
                    </motion.div>
                        </>
                    )}
                </div>

                {/* Untracked Cash Summary Section */}
                {isCashLoading ? (
                    <div className="glass-card p-6 animate-pulse">
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center space-x-4">
                                <div className="w-14 h-14 rounded-2xl bg-mono-200" />
                                <div>
                                    <div className="h-6 bg-mono-200 rounded w-40 mb-2" />
                                    <div className="h-4 bg-mono-100 rounded w-48" />
                                </div>
                            </div>
                            <div className="h-8 bg-mono-200 rounded w-32" />
                        </div>
                    </div>
                ) : cashData && cashData.estimated_untracked_cash > 0 ? (
                    <motion.div
                        className="glass-card p-6 border-l-4 border-l-mono-900"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center space-x-4">
                                <div className="w-14 h-14 rounded-2xl bg-mono-100 flex items-center justify-center">
                                    <Banknote className="w-7 h-7 text-mono-700" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-mono-900 mb-1">Untracked Cash</h3>
                                    <p className="text-sm text-mono-500">
                                        {cashData.days_since_withdrawal !== null 
                                            ? `${cashData.days_since_withdrawal} days since last ATM withdrawal`
                                            : 'Cash reconciliation status'
                                        }
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-3xl font-bold text-mono-900">
                                    {formatCurrency(cashData.estimated_untracked_cash)}
                                </p>
                                <p className="text-xs text-mono-500 mt-1">Estimated unaccounted</p>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                            <div className="bg-mono-50 rounded-lg p-4 border border-mono-200">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-mono-500 font-medium">Total Withdrawn</p>
                                    <ArrowUpRight className="w-4 h-4 text-mono-700" />
                                </div>
                                <p className="text-xl font-bold text-mono-900">{formatCurrency(cashData.total_withdrawn)}</p>
                            </div>
                            <div className="bg-mono-50 rounded-lg p-4 border border-mono-200">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-mono-500 font-medium">Tracked Spending</p>
                                    <TrendingDown className="w-4 h-4 text-mono-600" />
                                </div>
                                <p className="text-xl font-bold text-mono-900">{formatCurrency(cashData.tracked_cash_spend)}</p>
                            </div>
                            <div className="bg-mono-100 rounded-lg p-4 border border-mono-300">
                                <div className="flex items-center justify-between mb-2">
                                    <p className="text-xs text-mono-600 font-medium">Untracked Amount</p>
                                    <Wallet className="w-4 h-4 text-mono-700" />
                                </div>
                                <p className="text-xl font-bold text-mono-900">{formatCurrency(cashData.estimated_untracked_cash)}</p>
                            </div>
                        </div>

                        {/* Progress Bar */}
                        <div className="mb-4">
                            <div className="flex justify-between text-xs text-mono-500 mb-2">
                                <span>Cash Flow Tracking</span>
                                <span>{cashData.total_withdrawn > 0 ? Math.round((cashData.tracked_cash_spend / cashData.total_withdrawn) * 100) : 0}% tracked</span>
                            </div>
                            <div className="h-2 bg-mono-100 rounded-full overflow-hidden">
                                <div 
                                    className="h-full bg-mono-900 rounded-full transition-all duration-500"
                                    style={{ width: `${cashData.total_withdrawn > 0 ? Math.min((cashData.tracked_cash_spend / cashData.total_withdrawn) * 100, 100) : 0}%` }}
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-4 border-t border-mono-200">
                            <p className="text-sm text-mono-500">
                                💡 Add missing cash expenses to improve tracking accuracy
                            </p>
                            <button 
                                onClick={() => setIsModalOpen(true)}
                                className="btn-primary text-sm py-2 px-4"
                            >
                                Track Cash Expense
                            </button>
                        </div>
                    </motion.div>
                ) : cashData && cashData.estimated_untracked_cash === 0 ? (
                    <motion.div
                        className="glass-card p-6 border-l-4 border-l-green-500"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                                    <Wallet className="w-6 h-6 text-green-600" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-mono-900">All Cash Tracked! 🎉</h3>
                                    <p className="text-sm text-mono-500">You've accounted for all your cash withdrawals</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-2xl font-bold text-green-600">{formatCurrency(0)}</p>
                                <p className="text-xs text-mono-500">Untracked</p>
                            </div>
                        </div>
                    </motion.div>
                ) : null}

                {/* Untracked Cash Widget */}
                <UntrackedCashWidget 
                    key={widgetKey}
                    onTransactionAdded={() => {
                        dispatch(fetchTransactions({}))
                        dispatch(fetchTransactionStats('month'))
                        fetchCashData() // Refresh cash data
                    }}
                />

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Main Transaction List */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Filters */}
                        <div className="glass-card p-4 flex flex-col sm:flex-row gap-4 justify-between items-center">
                            <div className="relative w-full sm:w-64">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                <input
                                    type="text"
                                    placeholder="Search transactions..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full pl-9 pr-4 py-2 bg-gray-100 border border-gray-300 rounded-lg text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:border-gray-900"
                                />
                            </div>
                            <div className="flex items-center space-x-2 w-full sm:w-auto overflow-x-auto">
                                {['All', 'Essentials', 'Needs', 'Spends', 'Bills', 'Savings', 'Income', 'Other'].map((cat) => (
                                    <button
                                        key={cat}
                                        onClick={() => setSelectedCategory(cat)}
                                        className={`px-3 py-1.5 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${selectedCategory === cat
                                            ? 'bg-gray-900 text-white'
                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
                                            }`}
                                    >
                                        {cat}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* List */}
                        <div className="glass-card overflow-hidden">
                            {isLoading && isInitialLoad ? (
                                <TransactionSkeleton />
                            ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead>
                                        <tr className="border-b border-gray-200 bg-gray-50">
                                            <th className="px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">Transaction</th>
                                            <th className="px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">Category</th>
                                            <th className="px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
                                            <th className="px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider text-right">Amount</th>
                                            <th className="px-6 py-4 text-xs font-semibold text-gray-600 uppercase tracking-wider text-center">Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {filteredTransactions.length > 0 ? (
                                            filteredTransactions.map((t: any) => (
                                                <tr key={t.id} className="hover:bg-gray-50 transition-colors">
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <div className="flex items-center space-x-3">
                                                            <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-lg">
                                                                {getCategoryIcon(t.category)}
                                                            </div>
                                                            <span className="font-medium text-gray-900">{t.merchant || t.description || 'Transaction'}</span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap">
                                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${t.transaction_type === 'credit' || t.type === 'credit' ? 'bg-green-500/20 text-green-400' : 'bg-slate-700 text-slate-300'
                                                            }`}>
                                                            {t.category || 'Uncategorized'}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                        {formatDate(t.transaction_date || t.date)}
                                                    </td>
                                                    <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold text-right ${t.transaction_type === 'credit' || t.type === 'credit' ? 'text-green-600' : 'text-gray-700'
                                                        }`}>
                                                        {t.transaction_type === 'credit' || t.type === 'credit' ? '+' : '-'}{formatCurrency(t.amount)}
                                                    </td>
                                                    <td className="px-6 py-4 whitespace-nowrap text-center">
                                                        <button
                                                            onClick={() => handleHideTransaction(t.id)}
                                                            className="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                                                            title="Hide transaction"
                                                        >
                                                            <EyeOff className="w-4 h-4" />
                                                        </button>
                                                    </td>
                                                </tr>
                                            ))
                                        ) : (
                                            <tr>
                                                <td colSpan={5} className="px-6 py-12 text-center">
                                                    <CreditCard className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                                                    <p className="text-gray-600">No transactions found</p>
                                                    <p className="text-sm text-gray-400 mt-1">Add your first transaction to get started</p>
                                                </td>
                                            </tr>
                                        )}
                                    </tbody>
                                </table>
                            </div>
                            )}
                        </div>
                    </div>

                    {/* Sidebar - Recurring Payments */}
                    <div className="space-y-6">
                        <div className="glass-card p-6 bg-gradient-to-br from-slate-900 to-slate-800 border-l-4 border-l-primary-500">
                            <div className="flex items-center space-x-3 mb-6">
                                <div className="p-2 bg-primary-500/20 rounded-lg">
                                    <RefreshCcw className="w-6 h-6 text-primary-400" />
                                </div>
                                <div>
                                    <h2 className="text-lg font-bold text-white">Recurring Hub</h2>
                                    <p className="text-xs text-slate-400">Detected subscriptions & bills</p>
                                </div>
                            </div>

                            <div className="space-y-4">
                                {recurringPayments.length > 0 ? recurringPayments.map((payment: any) => (
                                    <div key={payment.id} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-primary-500/50 transition-colors group">
                                        <div className="flex justify-between items-start mb-2">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center group-hover:bg-primary-500/20 transition-colors text-lg">
                                                    {getCategoryIcon(payment.category)}
                                                </div>
                                                <div>
                                                    <p className="font-medium text-white text-sm">{payment.merchant || payment.description || 'Recurring'}</p>
                                                    <p className="text-xs text-slate-500">{payment.category || 'Monthly'}</p>
                                                </div>
                                            </div>
                                            <span className="font-bold text-white text-sm">{formatCurrency(payment.amount)}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-xs w-full mt-2 pt-2 border-t border-slate-700/50">
                                            <span className="text-slate-500">Next Due:</span>
                                            <span className="text-primary-300 bg-primary-500/10 px-2 py-0.5 rounded">{formatDate(payment.transaction_date || payment.date)}</span>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center py-6 text-slate-500">
                                        <RefreshCcw className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                        <p className="text-sm">No recurring payments detected</p>
                                    </div>
                                )}
                            </div>

                            <button className="w-full mt-6 btn-secondary text-xs py-2">
                                Scan for more
                            </button>
                        </div>

                        {/* Quick Actions */}
                        <div className="glass-card p-6">
                            <h3 className="text-sm font-semibold text-gray-900 mb-4">Quick Actions</h3>
                            <div className="grid grid-cols-2 gap-3">
                                <button className="p-3 rounded-xl bg-gray-100 hover:bg-gray-200 text-center transition-colors">
                                    <CreditCard className="w-5 h-5 text-purple-600 mx-auto mb-2" />
                                    <span className="text-xs text-gray-600">Pay Bill</span>
                                </button>
                                <button className="p-3 rounded-xl bg-gray-100 hover:bg-gray-200 text-center transition-colors">
                                    <Calendar className="w-5 h-5 text-orange-500 mx-auto mb-2" />
                                    <span className="text-xs text-gray-600">Schedule</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Add Transaction Modal */}
                <AddTransactionModal 
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSuccess={() => {
                        dispatch(fetchTransactions({}))
                        dispatch(fetchTransactionStats('month'))
                        setWidgetKey(prev => prev + 1) // Force widget refresh
                        fetchCashData() // Refresh cash data
                    }}
                />
            </div>
        </DashboardLayout>
    )
}
