'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    X,
    TrendingUp,
    Shield,
    Calculator,
    Calendar,
    Target,
    AlertTriangle,
    ChevronRight,
    Info,
    PieChart,
    BarChart3,
    ArrowUpRight,
    Clock
} from 'lucide-react'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { MarkdownRenderer } from '@/components/common/MarkdownRenderer'

interface ProjectionYear {
    year: number
    invested: number
    value: number
    returns: number
}

interface InvestmentModalProps {
    isOpen: boolean
    onClose: () => void
    item: any
    type: 'growth' | 'safety'
    monthlySurplus: number
}

export function InvestmentModal({ isOpen, onClose, item, type, monthlySurplus }: InvestmentModalProps) {
    const [investmentAmount, setInvestmentAmount] = useState<number>(10000)
    const [investmentYears, setInvestmentYears] = useState<number>(5)
    const [projections, setProjections] = useState<ProjectionYear[]>([])

    // Calculate projections whenever inputs change
    useEffect(() => {
        if (!item) return
        calculateProjections()
    }, [investmentAmount, investmentYears, item])

    const calculateProjections = () => {
        if (!item) return

        const rate = type === 'growth'
            ? (item.return || item.expected_return || 12) / 100
            : (item.rate || item.interest_rate || 7) / 100

        const newProjections: ProjectionYear[] = []

        for (let year = 1; year <= investmentYears; year++) {
            // For SIP/monthly investments
            if (item.type === 'SIP' || item.type === 'RD') {
                // Future Value of Annuity formula: FV = P * [((1 + r/12)^(n*12) - 1) / (r/12)] * (1 + r/12)
                const monthlyRate = rate / 12
                const months = year * 12
                const fv = investmentAmount * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate)
                const totalInvested = investmentAmount * months
                newProjections.push({
                    year,
                    invested: totalInvested,
                    value: Math.round(fv),
                    returns: Math.round(fv - totalInvested)
                })
            } else {
                // Lump sum: FV = PV * (1 + r)^n
                const fv = investmentAmount * Math.pow(1 + rate, year)
                newProjections.push({
                    year,
                    invested: investmentAmount,
                    value: Math.round(fv),
                    returns: Math.round(fv - investmentAmount)
                })
            }
        }

        setProjections(newProjections)
    }

    const getSuggestedAllocation = () => {
        const allocation = item?.allocation || 0
        return Math.round(monthlySurplus * allocation / 100)
    }

    const getRiskLevel = () => {
        if (type === 'safety') return { level: 'Low', color: 'text-green-400', bg: 'bg-green-500/20' }
        
        const returnRate = item?.return || item?.expected_return || 0
        if (returnRate > 15) return { level: 'High', color: 'text-red-400', bg: 'bg-red-500/20' }
        if (returnRate > 12) return { level: 'Medium', color: 'text-yellow-400', bg: 'bg-yellow-500/20' }
        return { level: 'Low-Medium', color: 'text-blue-400', bg: 'bg-blue-500/20' }
    }

    const getLockInPeriod = () => {
        if (type === 'safety') return item?.duration || 'Flexible'
        if (item?.type === 'Mutual Fund' || item?.type === 'SIP') return 'None (ELSS: 3 years)'
        if (item?.type === 'Stock' || item?.type === 'ETF') return 'None'
        return 'Variable'
    }

    const getTaxImplications = () => {
        if (type === 'safety') {
            if (item?.type === 'Gov Scheme') return 'Tax benefits under 80C (up to ₹1.5L)'
            if (item?.type === 'FD' || item?.type === 'RD') return 'Interest taxable as per income slab'
            return 'Tax as per applicable rules'
        }
        // Growth
        if (item?.type === 'Mutual Fund' || item?.type === 'SIP') {
            return 'LTCG >₹1L taxed at 10% (equity), STCG at 15%'
        }
        if (item?.type === 'Stock' || item?.type === 'ETF') {
            return 'LTCG >₹1L taxed at 10%, STCG at 15%'
        }
        return 'Tax as per applicable rules'
    }

    const risk = getRiskLevel()
    const finalProjection = projections[projections.length - 1]

    if (!item) return null

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                        onClick={onClose}
                    />

                    {/* Modal - Centered */}
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-white border border-mono-200 rounded-2xl shadow-2xl"
                        >
                            {/* Header */}
                            <div className="sticky top-0 p-6 border-b border-mono-200 bg-mono-50 rounded-t-2xl">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className="p-2 rounded-lg bg-mono-100">
                                            {type === 'growth' ? (
                                                <TrendingUp className="w-6 h-6 text-mono-700" />
                                            ) : (
                                                <Shield className="w-6 h-6 text-mono-700" />
                                            )}
                                        </div>
                                        <div>
                                            <span className="text-xs px-2 py-0.5 rounded bg-mono-200 text-mono-600">
                                                {item.type}
                                            </span>
                                            <h2 className="text-xl font-bold text-mono-900 mt-1">{item.name}</h2>
                                        </div>
                                    </div>
                                    <button
                                        onClick={onClose}
                                        className="p-2 hover:bg-mono-200 rounded-lg transition-colors"
                                    >
                                        <X className="w-5 h-5 text-mono-500" />
                                    </button>
                                </div>
                            </div>

                            <div className="p-6 space-y-6">
                                {/* Key Metrics */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                    <div className="glass-card p-4 text-center">
                                        <p className="text-xs text-mono-500 uppercase">Expected Return</p>
                                        <p className="text-2xl font-bold text-green-600">
                                            {type === 'growth' ? `${item.return || item.expected_return}%` : `${item.rate || item.interest_rate}%`}
                                        </p>
                                        <p className="text-xs text-mono-400">{type === 'growth' ? 'CAGR' : 'p.a.'}</p>
                                    </div>
                                    <div className="glass-card p-4 text-center">
                                        <p className="text-xs text-mono-500 uppercase">Risk Level</p>
                                        <p className={`text-lg font-semibold ${risk.level === 'Low' ? 'text-green-600' : risk.level === 'Medium' ? 'text-yellow-600' : 'text-red-600'}`}>{risk.level}</p>
                                        <div className={`mt-1 mx-auto w-8 h-1 rounded ${risk.level === 'Low' ? 'bg-green-500' : risk.level === 'Medium' ? 'bg-yellow-500' : 'bg-red-500'}`}></div>
                                    </div>
                                    <div className="glass-card p-4 text-center">
                                        <p className="text-xs text-mono-500 uppercase">Lock-in</p>
                                        <p className="text-lg font-semibold text-mono-900">{getLockInPeriod()}</p>
                                    </div>
                                    <div className="glass-card p-4 text-center">
                                        <p className="text-xs text-mono-500 uppercase">Suggested</p>
                                        <p className="text-lg font-bold text-mono-900">{formatCurrency(getSuggestedAllocation())}</p>
                                        <p className="text-xs text-mono-400">{item.allocation}% allocation</p>
                                    </div>
                                </div>

                            {/* Rationale */}
                            <div className="glass-card p-4">
                                <div className="flex items-center space-x-2 mb-2">
                                    <Info className="w-4 h-4 text-mono-600" />
                                    <h3 className="font-semibold text-mono-900">Why This Investment?</h3>
                                </div>
                                <p className="text-mono-600 text-sm">
                                    {item.rationale || 'Based on your risk profile and market conditions, this investment offers a good balance of risk and returns.'}
                                </p>
                            </div>

                            {/* Investment Calculator */}
                            <div className="glass-card p-4">
                                <div className="flex items-center space-x-2 mb-4">
                                    <Calculator className="w-5 h-5 text-mono-700" />
                                    <h3 className="font-semibold text-mono-900">Investment Calculator</h3>
                                </div>

                                <div className="grid md:grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label className="text-xs text-mono-500 uppercase mb-1 block">
                                            {item.type === 'SIP' || item.type === 'RD' ? 'Monthly Investment' : 'Investment Amount'}
                                        </label>
                                        <div className="relative">
                                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-mono-400">₹</span>
                                            <input
                                                type="number"
                                                value={investmentAmount}
                                                onChange={(e) => setInvestmentAmount(Number(e.target.value))}
                                                className="w-full bg-mono-50 border border-mono-300 rounded-lg px-8 py-2 text-mono-900 focus:border-mono-900 focus:outline-none"
                                            />
                                        </div>
                                        <div className="flex gap-2 mt-2">
                                            {[5000, 10000, 25000, 50000].map((amt) => (
                                                <button
                                                    key={amt}
                                                    onClick={() => setInvestmentAmount(amt)}
                                                    className={`text-xs px-2 py-1 rounded ${investmentAmount === amt ? 'bg-mono-900 text-white' : 'bg-mono-100 text-mono-600 hover:bg-mono-200'}`}
                                                >
                                                    {amt >= 1000 ? `${amt / 1000}K` : amt}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                    <div>
                                        <label className="text-xs text-mono-500 uppercase mb-1 block">Investment Period (Years)</label>
                                        <input
                                            type="range"
                                            min="1"
                                            max="30"
                                            value={investmentYears}
                                            onChange={(e) => setInvestmentYears(Number(e.target.value))}
                                            className="w-full accent-mono-900"
                                        />
                                        <div className="flex justify-between text-xs text-mono-500 mt-1">
                                            <span>1 Year</span>
                                            <span className="text-mono-900 font-semibold">{investmentYears} Years</span>
                                            <span>30 Years</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Projection Results */}
                                {finalProjection && (
                                    <div className="grid grid-cols-3 gap-4 p-4 bg-mono-50 rounded-lg border border-mono-200">
                                        <div className="text-center">
                                            <p className="text-xs text-mono-500">Total Invested</p>
                                            <p className="text-lg font-bold text-mono-900">{formatCurrency(finalProjection.invested)}</p>
                                        </div>
                                        <div className="text-center border-x border-mono-200">
                                            <p className="text-xs text-mono-500">Est. Returns</p>
                                            <p className="text-lg font-bold text-green-600">+{formatCurrency(finalProjection.returns)}</p>
                                        </div>
                                        <div className="text-center">
                                            <p className="text-xs text-mono-500">Maturity Value</p>
                                            <p className="text-lg font-bold text-mono-900">{formatCurrency(finalProjection.value)}</p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Year-wise Projection Table */}
                            <div className="glass-card p-4">
                                <div className="flex items-center space-x-2 mb-4">
                                    <BarChart3 className="w-5 h-5 text-mono-700" />
                                    <h3 className="font-semibold text-mono-900">Year-wise Projection</h3>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-sm">
                                        <thead>
                                            <tr className="text-mono-500 border-b border-mono-200">
                                                <th className="text-left py-2">Year</th>
                                                <th className="text-right py-2">Invested</th>
                                                <th className="text-right py-2">Returns</th>
                                                <th className="text-right py-2">Total Value</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {projections.map((proj) => (
                                                <tr key={proj.year} className="border-b border-mono-100 hover:bg-mono-50">
                                                    <td className="py-2 text-mono-700">Year {proj.year}</td>
                                                    <td className="py-2 text-right text-mono-600">{formatCurrency(proj.invested)}</td>
                                                    <td className="py-2 text-right text-green-600">+{formatCurrency(proj.returns)}</td>
                                                    <td className="py-2 text-right font-semibold text-mono-900">{formatCurrency(proj.value)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

                            {/* Tax & Additional Info */}
                            <div className="grid md:grid-cols-2 gap-4">
                                <div className="glass-card p-4">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                                        <h3 className="font-semibold text-mono-900 text-sm">Tax Implications</h3>
                                    </div>
                                    <p className="text-mono-600 text-xs">{getTaxImplications()}</p>
                                </div>
                                <div className="glass-card p-4">
                                    <div className="flex items-center space-x-2 mb-2">
                                        <Clock className="w-4 h-4 text-mono-600" />
                                        <h3 className="font-semibold text-mono-900 text-sm">Best For</h3>
                                    </div>
                                    <p className="text-mono-600 text-xs">
                                        {type === 'growth'
                                            ? 'Long-term wealth creation, beating inflation, achieving financial goals'
                                            : 'Capital preservation, regular income, emergency fund, short-term goals'}
                                    </p>
                                </div>
                            </div>

                            {/* Disclaimer */}
                            <p className="text-xs text-mono-400 text-center">
                                * Projections are indicative based on historical returns. Actual returns may vary. 
                                Please consult a financial advisor before investing.
                            </p>
                        </div>
                    </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    )
}
