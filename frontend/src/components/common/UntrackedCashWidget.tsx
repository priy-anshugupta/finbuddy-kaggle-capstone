'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Wallet, TrendingUp, Plus, X, Loader2 } from 'lucide-react'

interface CashSuggestion {
    label: string
    subcategory: string
    typical_amount: number
    amount_range: { low: number; high: number }
    probability: number
}

interface CashCheckData {
    estimated_untracked_cash: number
    total_withdrawn: number
    tracked_cash_spend: number
    days_since_withdrawal: number | null
    suggestions: CashSuggestion[]
}

interface UntrackedCashWidgetProps {
    onTransactionAdded?: () => void
}

export function UntrackedCashWidget({ onTransactionAdded }: UntrackedCashWidgetProps = {}) {
    const [cashData, setCashData] = useState<CashCheckData | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isExpanded, setIsExpanded] = useState(false)
    const [isSubmitting, setIsSubmitting] = useState(false)

    useEffect(() => {
        fetchCashCheck()
    }, [])

    const fetchCashCheck = async () => {
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
            console.error('Error fetching cash check:', error)
        } finally {
            setIsLoading(false)
        }
    }

    const handleQuickAdd = async (suggestion: CashSuggestion) => {
        setIsSubmitting(true)
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/cash-check/quick-add`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    amount: suggestion.typical_amount,
                    subcategory: suggestion.subcategory,
                    description: `Cash - ${suggestion.label}`,
                }),
            })

            if (response.ok) {
                // Refresh cash check data
                await fetchCashCheck()
                setIsExpanded(false)
                // Notify parent component
                if (onTransactionAdded) {
                    onTransactionAdded()
                }
            } else {
                alert('Failed to add expense')
            }
        } catch (error) {
            console.error('Error adding expense:', error)
            alert('Failed to add expense')
        } finally {
            setIsSubmitting(false)
        }
    }

    if (isLoading) {
        return (
            <div className="glass-card p-6 animate-pulse">
                <div className="h-4 bg-mono-200 rounded w-32 mb-4" />
                <div className="h-8 bg-mono-200 rounded w-24" />
            </div>
        )
    }

    if (!cashData || cashData.estimated_untracked_cash < 100) {
        return null // Don't show if no untracked cash
    }

    // Calculate tracking percentage safely to avoid NaN
    const trackingPercentage = cashData.total_withdrawn > 0 
        ? Math.min(100, (cashData.tracked_cash_spend / cashData.total_withdrawn) * 100)
        : 0

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 border-l-4 border-l-mono-900"
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-xl bg-mono-100 flex items-center justify-center">
                        <Wallet className="w-5 h-5 text-mono-700" />
                    </div>
                    <div>
                        <h3 className="text-sm font-semibold text-mono-900">Untracked Cash</h3>
                        <p className="text-xs text-mono-500">
                            {cashData.days_since_withdrawal !== null 
                                ? `${cashData.days_since_withdrawal} days since withdrawal`
                                : 'Cash reconciliation status'
                            }
                        </p>
                    </div>
                </div>
                {!isExpanded && (
                    <button
                        onClick={() => setIsExpanded(true)}
                        className="text-mono-700 hover:text-mono-900 text-sm font-medium transition-colors"
                    >
                        Quick Add
                    </button>
                )}
            </div>

            {/* Amount Display */}
            <div className="mb-4">
                <p className="text-3xl font-bold text-mono-900">
                    ₹{cashData.estimated_untracked_cash.toLocaleString('en-IN')}
                </p>
                <p className="text-sm text-mono-500 mt-1">
                    Tracked: ₹{cashData.tracked_cash_spend.toLocaleString('en-IN')} of ₹
                    {cashData.total_withdrawn.toLocaleString('en-IN')}
                </p>
            </div>

            {/* Suggestions (Expanded) */}
            {isExpanded && (
                <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="border-t border-mono-200 pt-4 space-y-2"
                >
                    <div className="flex items-center justify-between mb-3">
                        <p className="text-xs text-mono-500 font-medium">Common expenses:</p>
                        <button
                            onClick={() => setIsExpanded(false)}
                            className="text-mono-400 hover:text-mono-900"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>

                    {cashData.suggestions.map((suggestion, idx) => (
                        <button
                            key={idx}
                            onClick={() => handleQuickAdd(suggestion)}
                            disabled={isSubmitting}
                            className="w-full flex items-center justify-between p-3 rounded-lg bg-mono-50 hover:bg-mono-100 border border-mono-200 hover:border-mono-400 transition-all group disabled:opacity-50"
                        >
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 rounded-lg bg-mono-100 flex items-center justify-center group-hover:bg-mono-200 transition-colors">
                                    <Plus className="w-4 h-4 text-mono-700" />
                                </div>
                                <div className="text-left">
                                    <p className="text-sm font-medium text-mono-900">{suggestion.label}</p>
                                    <p className="text-xs text-mono-500">
                                        ₹{suggestion.amount_range.low}-₹{suggestion.amount_range.high} typical
                                    </p>
                                </div>
                            </div>
                            <span className="text-lg font-bold text-mono-900">
                                ₹{suggestion.typical_amount}
                            </span>
                        </button>
                    ))}

                    <button
                        onClick={() => setIsExpanded(false)}
                        className="w-full mt-2 py-2 text-xs text-mono-500 hover:text-mono-900 transition-colors"
                    >
                        I still have this cash in my wallet
                    </button>
                </motion.div>
            )}

            {/* Progress Bar */}
            {!isExpanded && (
                <div className="mt-4">
                    <div className="flex justify-between text-xs text-mono-500 mb-2">
                        <span>Cash Flow Tracking</span>
                        <span>{Math.round(trackingPercentage)}% tracked</span>
                    </div>
                    <div className="h-2 bg-mono-100 rounded-full overflow-hidden">
                        <motion.div
                            initial={{ width: 0 }}
                            animate={{
                                width: `${trackingPercentage}%`,
                            }}
                            className="h-full bg-mono-900"
                        />
                    </div>
                </div>
            )}
        </motion.div>
    )
}
