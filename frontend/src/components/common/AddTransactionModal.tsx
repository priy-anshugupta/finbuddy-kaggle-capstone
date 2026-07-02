'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Calendar, DollarSign, Tag, FileText, Loader2 } from 'lucide-react'

interface AddTransactionModalProps {
    isOpen: boolean
    onClose: () => void
    onSuccess?: () => void
}

export function AddTransactionModal({ isOpen, onClose, onSuccess }: AddTransactionModalProps) {
    const [isSubmitting, setIsSubmitting] = useState(false)
    const [formData, setFormData] = useState({
        amount: '',
        transaction_type: 'debit',
        category: 'other',
        subcategory: '',
        description: '',
        transaction_date: new Date().toISOString().split('T')[0],
        tags: ['cash', 'cash_spend'],
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setIsSubmitting(true)

        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/transactions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    ...formData,
                    amount: parseFloat(formData.amount),
                    transaction_date: new Date(formData.transaction_date).toISOString(),
                }),
            })

            if (response.ok) {
                onSuccess?.()
                onClose()
                // Reset form
                setFormData({
                    amount: '',
                    transaction_type: 'debit',
                    category: 'other',
                    subcategory: '',
                    description: '',
                    transaction_date: new Date().toISOString().split('T')[0],
                    tags: ['cash', 'cash_spend'],
                })
            } else {
                const error = await response.json()
                alert(`Failed to add transaction: ${error.detail || 'Unknown error'}`)
            }
        } catch (error) {
            console.error('Error adding transaction:', error)
            alert('Failed to add transaction. Please try again.')
        } finally {
            setIsSubmitting(false)
        }
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
                    onClick={onClose}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="glass-card p-6 w-full max-w-md"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-white">Add Transaction</h2>
                            <button
                                onClick={onClose}
                                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
                            >
                                <X className="w-5 h-5 text-slate-400" />
                            </button>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* Transaction Type */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Type</label>
                                <div className="flex space-x-2">
                                    <button
                                        type="button"
                                        onClick={() => setFormData({ ...formData, transaction_type: 'debit' })}
                                        className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                                            formData.transaction_type === 'debit'
                                                ? 'bg-red-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:text-white'
                                        }`}
                                    >
                                        Expense
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setFormData({ ...formData, transaction_type: 'credit' })}
                                        className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                                            formData.transaction_type === 'credit'
                                                ? 'bg-green-500 text-white'
                                                : 'bg-slate-800 text-slate-400 hover:text-white'
                                        }`}
                                    >
                                        Income
                                    </button>
                                </div>
                            </div>

                            {/* Amount */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Amount (₹)
                                </label>
                                <div className="relative">
                                    <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <input
                                        type="number"
                                        step="0.01"
                                        required
                                        value={formData.amount}
                                        onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                                        placeholder="0.00"
                                    />
                                </div>
                            </div>

                            {/* Category */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Category</label>
                                <div className="relative">
                                    <Tag className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <select
                                        value={formData.category}
                                        onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                                    >
                                        <option value="other">Other</option>
                                        <option value="needs">Needs</option>
                                        <option value="essentials">Essentials</option>
                                        <option value="spends">Spends</option>
                                        <option value="bills">Bills</option>
                                        <option value="savings">Savings</option>
                                        <option value="investments">Investments</option>
                                        <option value="income">Income</option>
                                    </select>
                                </div>
                            </div>

                            {/* Subcategory */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Subcategory (Optional)
                                </label>
                                <input
                                    type="text"
                                    value={formData.subcategory}
                                    onChange={(e) => setFormData({ ...formData, subcategory: e.target.value })}
                                    className="w-full px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                                    placeholder="e.g., groceries, transport"
                                />
                            </div>

                            {/* Description */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">
                                    Description (Optional)
                                </label>
                                <div className="relative">
                                    <FileText className="absolute left-3 top-3 w-5 h-5 text-slate-500" />
                                    <textarea
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                                        rows={3}
                                        placeholder="Add details..."
                                    />
                                </div>
                            </div>

                            {/* Date */}
                            <div>
                                <label className="block text-sm font-medium text-slate-300 mb-2">Date</label>
                                <div className="relative">
                                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                                    <input
                                        type="date"
                                        required
                                        value={formData.transaction_date}
                                        onChange={(e) => setFormData({ ...formData, transaction_date: e.target.value })}
                                        className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
                                    />
                                </div>
                            </div>

                            {/* Submit Button */}
                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="flex-1 py-2 px-4 bg-slate-800 hover:bg-slate-700 text-white rounded-lg font-medium transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="flex-1 py-2 px-4 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                                >
                                    {isSubmitting ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                                            Adding...
                                        </>
                                    ) : (
                                        'Add Transaction'
                                    )}
                                </button>
                            </div>
                        </form>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}
