'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    TrendingUp,
    Shield,
    Zap,
    PieChart,
    BarChart,
    Target,
    ArrowRight,
    Info,
    ExternalLink,
    ChevronDown,
    LineChart,
    Loader2,
    Star,
    Award,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { formatCurrency, formatPercentage } from '@/lib/utils'
import { useAppDispatch, useAppSelector, RootState } from '@/store/hooks'
import { fetchInvestments, fetchAgentInsights } from '@/store/slices/investmentsSlice'
import { InvestmentModal } from '@/components/investments/InvestmentModal'
import { MarkdownRenderer } from '@/components/common/MarkdownRenderer'

export default function InvestmentsPage() {
    const dispatch = useAppDispatch()
    const { portfolio, agentInsights, isLoadingInsights, error } = useAppSelector((state: any) => state.investments)
    const [activeTab, setActiveTab] = useState<'growth' | 'safety'>('growth')
    const [selectedItem, setSelectedItem] = useState<any>(null)
    const [modalType, setModalType] = useState<'growth' | 'safety'>('growth')
    const [isModalOpen, setIsModalOpen] = useState(false)

    // Fetch AI insights on mount
    useEffect(() => {
        dispatch(fetchAgentInsights(undefined))
    }, [dispatch])

    const handleRegenerate = () => {
        dispatch(fetchAgentInsights(undefined))
    }

    const handleItemClick = (item: any, type: 'growth' | 'safety') => {
        setSelectedItem(item)
        setModalType(type)
        setIsModalOpen(true)
    }

    const normalizeRecommendations = (input: any) => {
        if (Array.isArray(input)) {
            return input
        }

        if (Array.isArray(input?.recommendations)) {
            return input.recommendations
        }

        if (Array.isArray(input?.items)) {
            return input.items
        }

        return []
    }

    const analysis = typeof agentInsights?.analysis === 'object' && agentInsights?.analysis !== null
        ? agentInsights.analysis
        : null

    // Extract data from agent insights or use defaults
    const analysisdata = analysis ? {
        monthlySurplus: analysis.monthly_surplus || 15000,
        riskScore: analysis.risk_score || 65,
        riskProfile: analysis.risk_profile || 'Moderate Growth',
        marketSentiment: analysis.market_sentiment || 'Neutral',
        topTrends: analysis.top_trends || ['Market Analysis', 'Portfolio Review', 'Risk Assessment'],
    } : {
        monthlySurplus: 15000,
        riskScore: 65,
        riskProfile: 'Moderate',
        marketSentiment: isLoadingInsights ? 'Analyzing...' : 'Neutral',
        topTrends: isLoadingInsights ? ['Loading...'] : ['Index Funds', 'Banking', 'Technology'],
    }

    const growthRecommendations = normalizeRecommendations(agentInsights?.growth_recommendations)
    const safetyRecommendations = normalizeRecommendations(agentInsights?.safety_recommendations)

    const getSentimentColor = (sentiment: string) => {
        const s = sentiment.toLowerCase()
        if (s.includes('bullish') || s.includes('positive')) return 'text-green-400'
        if (s.includes('bearish') || s.includes('negative')) return 'text-red-400'
        return 'text-yellow-400'
    }

    const getSentimentIcon = (sentiment: string) => {
        const s = sentiment.toLowerCase()
        if (s.includes('bullish') || s.includes('positive')) return <TrendingUp className="w-5 h-5" />
        if (s.includes('bearish') || s.includes('negative')) return <TrendingUp className="w-5 h-5 rotate-180" />
        return <TrendingUp className="w-5 h-5" />
    }

    return (
        <DashboardLayout>
            <div className="space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-mono-900">Investment Advisory</h1>
                        <p className="text-mono-500">AI-driven insights tailored to your spending & market trends.</p>
                    </div>
                    <button
                        onClick={handleRegenerate}
                        disabled={isLoadingInsights}
                        className="btn-primary flex items-center space-x-2 disabled:opacity-50"
                    >
                        {isLoadingInsights ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Zap className="w-4 h-4" />
                        )}
                        <span>{isLoadingInsights ? 'Generating...' : 'Regenerate Plan'}</span>
                    </button>
                </div>

                {/* Analysis Overview Card */}
                <div className="onyx-card p-6">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center md:text-left">
                        <div className="space-y-1">
                            <p className="text-xs text-mono-400 uppercase tracking-wider">Investable Surplus</p>
                            <h2 className="text-3xl font-bold text-green-400">
                                {formatCurrency(analysisdata.monthlySurplus)}
                            </h2>
                            <p className="text-xs text-mono-500">Available monthly from income</p>
                        </div>

                        <div className="space-y-1">
                            <p className="text-xs text-mono-400 uppercase tracking-wider">Risk Profile</p>
                            <div className="flex items-center justify-center md:justify-start space-x-2">
                                <span className="text-xl font-semibold text-white">{analysisdata.riskProfile}</span>
                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${analysisdata.riskScore > 60 ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'
                                    }`}>
                                    {analysisdata.riskScore}/100
                                </span>
                            </div>
                            <div className="w-full bg-mono-700 h-1.5 rounded-full mt-2">
                                <div
                                    className="bg-gradient-to-r from-green-500 to-orange-500 h-1.5 rounded-full transition-all duration-500"
                                    style={{ width: `${analysisdata.riskScore}%` }}
                                />
                            </div>
                        </div>

                        <div className="space-y-1">
                            <p className="text-xs text-mono-400 uppercase tracking-wider">Market Sentiment</p>
                            <div className={`flex items-center justify-center md:justify-start space-x-2 ${getSentimentColor(analysisdata.marketSentiment)}`}>
                                {getSentimentIcon(analysisdata.marketSentiment)}
                                <span className="text-xl font-semibold">{analysisdata.marketSentiment}</span>
                            </div>
                            <p className="text-xs text-mono-500">Based on recent news analysis</p>
                        </div>

                        <div className="space-y-2">
                            <p className="text-xs text-mono-400 uppercase tracking-wider">Top Trends</p>
                            <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                                {analysisdata.topTrends.slice(0, 3).map((trend: string) => (
                                    <span key={trend} className="px-2 py-1 bg-mono-800 border border-mono-700 rounded text-xs text-mono-200">
                                        {trend}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Split View: Growth vs Safety */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* Left Column: Growth Generators */}
                    <section className="space-y-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                                <div className="p-2 bg-gradient-to-br from-purple-600 to-blue-600 rounded-lg">
                                    <LineChart className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-mono-900">Growth Generators</h2>
                                    <p className="text-xs text-mono-500">High-potential equity & mutual funds</p>
                                </div>
                            </div>
                            <span className="text-xs text-mono-500 bg-mono-200 px-2 py-1 rounded">
                                Top {growthRecommendations.length} picks
                            </span>
                        </div>

                        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                            {isLoadingInsights ? (
                                <div className="glass-card p-8 flex flex-col items-center justify-center">
                                    <Loader2 className="w-8 h-8 animate-spin text-purple-500 mb-2" />
                                    <p className="text-mono-500 text-sm">Analyzing your portfolio...</p>
                                </div>
                            ) : growthRecommendations.length === 0 ? (
                                <div className="glass-card p-8 flex flex-col items-center justify-center">
                                    <TrendingUp className="w-12 h-12 text-mono-400 mb-2" />
                                    <p className="text-mono-500 text-sm text-center">
                                        {error
                                            ? `Unable to load growth recommendations (${error}). Please regenerate or sign in again.`
                                            : 'No recommendations yet. Add transactions to get personalized advice.'}
                                    </p>
                                </div>
                            ) : (
                                growthRecommendations.map((item: any, idx: number) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        onClick={() => handleItemClick(item, 'growth')}
                                        className="glass-card p-4 hover:border-purple-500/50 transition-all cursor-pointer group relative overflow-hidden"
                                    >
                                        {/* Rank Badge */}
                                        {idx < 3 && (
                                            <div className="absolute top-2 right-2">
                                                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${idx === 0 ? 'bg-yellow-500 text-black' :
                                                    idx === 1 ? 'bg-slate-300 text-black' :
                                                        'bg-orange-600 text-white'
                                                    }`}>
                                                    {idx + 1}
                                                </div>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-start">
                                            <div className="flex-1 pr-12">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <span className={`text-xs px-2 py-0.5 rounded border ${item.type === 'Stock' ? 'border-blue-500 text-blue-600 bg-blue-500/10' :
                                                        item.type === 'Mutual Fund' ? 'border-purple-500 text-purple-600 bg-purple-500/10' :
                                                            item.type === 'SIP' ? 'border-green-500 text-green-600 bg-green-500/10' :
                                                                item.type === 'ETF' ? 'border-cyan-500 text-cyan-600 bg-cyan-500/10' :
                                                                    'border-mono-400 text-mono-600 bg-mono-200'
                                                        }`}>{item.type}</span>
                                                    <h3 className="font-semibold text-mono-900 group-hover:text-purple-600 transition-colors line-clamp-1">{item.name}</h3>
                                                </div>
                                                <p className="text-sm text-mono-600 line-clamp-1">{item.rationale}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-green-600">+{item.return || item.expected_return}%</p>
                                                <p className="text-xs text-mono-500">Exp. CAGR</p>
                                            </div>
                                        </div>
                                        <div className="mt-3 flex items-center justify-between text-xs border-t border-mono-200 pt-2">
                                            {item.allocation > 0 ? (
                                                <span className="text-mono-500">
                                                    Allocation: <span className="text-mono-900 font-medium">{item.allocation}%</span>
                                                    <span className="text-purple-600 ml-1">({formatCurrency(analysisdata.monthlySurplus * item.allocation / 100)})</span>
                                                </span>
                                            ) : (
                                                <span className="text-mono-500">Alternative option</span>
                                            )}
                                            <span className="flex items-center text-purple-600 group-hover:text-purple-500">
                                                View Details <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
                                            </span>
                                        </div>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </section>

                    {/* Right Column: Safety Net */}
                    <section className="space-y-4">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                                <div className="p-2 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg">
                                    <Shield className="w-5 h-5 text-white" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold text-mono-900">Safety Net</h2>
                                    <p className="text-xs text-mono-500">Stable returns with FDs, RDs & PSUs</p>
                                </div>
                            </div>
                            <span className="text-xs text-mono-500 bg-mono-200 px-2 py-1 rounded">
                                Top {safetyRecommendations.length} picks
                            </span>
                        </div>

                        <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                            {isLoadingInsights ? (
                                <div className="glass-card p-8 flex flex-col items-center justify-center">
                                    <Loader2 className="w-8 h-8 animate-spin text-emerald-500 mb-2" />
                                    <p className="text-mono-500 text-sm">Loading safety options...</p>
                                </div>
                            ) : safetyRecommendations.length === 0 ? (
                                <div className="glass-card p-8 flex flex-col items-center justify-center">
                                    <Shield className="w-12 h-12 text-mono-400 mb-2" />
                                    <p className="text-mono-500 text-sm text-center">
                                        {error
                                            ? `Unable to load safety recommendations (${error}). Please regenerate or sign in again.`
                                            : 'No recommendations yet. Add transactions to get personalized advice.'}
                                    </p>
                                </div>
                            ) : (
                                safetyRecommendations.map((item: any, idx: number) => (
                                    <motion.div
                                        key={idx}
                                        initial={{ opacity: 0, x: 20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: idx * 0.05 }}
                                        onClick={() => handleItemClick(item, 'safety')}
                                        className="glass-card p-4 hover:border-emerald-500/50 transition-all cursor-pointer group relative overflow-hidden"
                                    >
                                        {/* Rank Badge */}
                                        {idx < 3 && (
                                            <div className="absolute top-2 right-2">
                                                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${idx === 0 ? 'bg-yellow-500 text-black' :
                                                    idx === 1 ? 'bg-slate-300 text-black' :
                                                        'bg-orange-600 text-white'
                                                    }`}>
                                                    {idx + 1}
                                                </div>
                                            </div>
                                        )}

                                        <div className="flex justify-between items-start">
                                            <div className="flex-1 pr-12">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <span className={`text-xs px-2 py-0.5 rounded border ${item.type === 'FD' ? 'border-emerald-500 text-emerald-600 bg-emerald-500/10' :
                                                        item.type === 'RD' ? 'border-teal-500 text-teal-600 bg-teal-500/10' :
                                                            item.type === 'Gov Scheme' ? 'border-orange-500 text-orange-600 bg-orange-500/10' :
                                                                item.type === 'PSU Bond' || item.type === 'Bond' ? 'border-blue-500 text-blue-600 bg-blue-500/10' :
                                                                    item.type === 'Debt Fund' ? 'border-indigo-500 text-indigo-600 bg-indigo-500/10' :
                                                                        'border-mono-400 text-mono-600 bg-mono-200'
                                                        }`}>{item.type}</span>
                                                    <h3 className="font-semibold text-mono-900 group-hover:text-emerald-600 transition-colors line-clamp-1">{item.name}</h3>
                                                </div>
                                                <div className="flex items-center space-x-4 mt-1">
                                                    <div className="text-xs">
                                                        <span className="text-mono-500">Duration: </span>
                                                        <span className="text-mono-700">{item.duration}</span>
                                                    </div>
                                                    <div className="text-xs">
                                                        <span className="text-mono-500">Safety: </span>
                                                        <span className="text-green-600">{item.safety}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-emerald-600">{item.rate || item.interest_rate}%</p>
                                                <p className="text-xs text-mono-500">Interest p.a.</p>
                                            </div>
                                        </div>
                                        <div className="mt-3 flex items-center justify-between text-xs border-t border-mono-200 pt-2">
                                            <span className="text-mono-500">
                                                Maturity: <span className="text-mono-900 font-medium">
                                                    {typeof item.maturityVal === 'number' || typeof item.maturity_value === 'number'
                                                        ? formatCurrency(item.maturityVal || item.maturity_value)
                                                        : (item.maturityVal || item.maturity_value || 'Variable')}
                                                </span>
                                            </span>
                                            <span className="flex items-center text-emerald-600 group-hover:text-emerald-500">
                                                View Plan <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
                                            </span>
                                        </div>
                                    </motion.div>
                                ))
                            )}
                        </div>
                    </section>

                </div>

                {/* Aggregated Advice */}
                {agentInsights?.aggregated_advice && (
                    <div className="glass-card p-4 border-l-4 border-blue-500">
                        <div className="flex items-start space-x-3">
                            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                                <h3 className="font-semibold text-mono-900 mb-2">AI Recommendation</h3>
                                <MarkdownRenderer content={agentInsights.aggregated_advice} />
                            </div>
                        </div>
                    </div>
                )}

                {/* Disclaimer */}
                <div className="text-center p-4">
                    <p className="text-xs text-mono-500">
                        Disclaimer: These recommendations are generated by AI based on your financial data and market trends.
                        Investments are subject to market risks. Please consult a certified financial advisor before making any decisions.
                    </p>
                </div>
            </div>

            {/* Investment Detail Modal */}
            <InvestmentModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                item={selectedItem}
                type={modalType}
                monthlySurplus={analysisdata.monthlySurplus}
            />
        </DashboardLayout>
    )
}
