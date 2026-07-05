'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
    ArrowRight,
    Bot,
    LineChart,
    Shield,
    Wallet,
    TrendingUp,
    PiggyBank,
    CreditCard,
    Sparkles,
    X,
    Check,
    Zap,
    Crown
} from 'lucide-react'
import { CardFan3D } from '@/components/animations'

const features = [
    {
        icon: Bot,
        title: 'AI-Powered Insights',
        description: 'Get personalized financial advice from our Gemini 2.5 Flash powered agents.',
    },
    {
        icon: LineChart,
        title: 'Investment Tracking',
        description: 'Track stocks, mutual funds, and get real-time market updates.',
    },
    {
        icon: Wallet,
        title: 'Smart Budgeting',
        description: 'Automatic categorization and spending analysis.',
    },
    {
        icon: Shield,
        title: 'Secure & Private',
        description: 'Bank-grade security for your financial data.',
    },
]

const stats = [
    { value: '50K+', label: 'Active Users' },
    { value: '₹100Cr+', label: 'Tracked' },
    { value: '99.9%', label: 'Uptime' },
    { value: '4.9★', label: 'Rating' },
]

const pricingPlans = [
    {
        name: 'Free',
        price: '₹0',
        period: 'forever',
        description: '7-day trial of Pro features included',
        icon: Zap,
        features: [
            'Basic expense tracking',
            'Up to 50 transactions/month',
            '3 AI agent interactions/day',
            'Basic investment tracking',
            'Email support',
        ],
        cta: 'Start Free Trial',
        popular: false,
    },
    {
        name: 'Pro Monthly',
        price: '₹299',
        period: '/month',
        description: 'Best for active users',
        icon: TrendingUp,
        features: [
            'Unlimited transactions',
            'Unlimited AI interactions',
            'All 13 AI agents access',
            'Advanced analytics & reports',
            'Priority support',
            'OCR receipt scanning',
            'Investment recommendations',
        ],
        cta: 'Subscribe Monthly',
        popular: true,
    },
    {
        name: 'Pro Annual',
        price: '₹2,499',
        period: '/year',
        description: 'Save ₹1,089 (30% off)',
        icon: Crown,
        features: [
            'Everything in Pro Monthly',
            '2 months free',
            'Early access to new features',
            'Dedicated account manager',
            'Custom financial reports',
            'API access',
            'White-glove onboarding',
        ],
        cta: 'Subscribe Yearly',
        popular: false,
    },
]

// Pricing Modal Component
function PricingModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div 
                        initial={{ opacity: 0 }} 
                        animate={{ opacity: 1 }} 
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100]" 
                        onClick={onClose} 
                    />
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 pointer-events-none">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }} 
                            animate={{ opacity: 1, scale: 1 }} 
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="w-full max-w-5xl max-h-[90vh] overflow-y-auto bg-white rounded-[24px] shadow-2xl border border-mono-200 pointer-events-auto"
                        >
                            {/* Header */}
                            <div className="sticky top-0 p-6 border-b border-mono-200 bg-white/95 backdrop-blur-sm rounded-t-[24px]">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-mono-900">Choose Your Plan</h2>
                                        <p className="text-mono-500 mt-1">Start free, upgrade when you're ready</p>
                                    </div>
                                    <button onClick={onClose} className="p-2 hover:bg-mono-100 rounded-xl transition-colors">
                                        <X className="w-6 h-6 text-mono-600" />
                                    </button>
                                </div>
                            </div>

                            {/* Pricing Cards */}
                            <div className="p-6">
                                <div className="grid md:grid-cols-3 gap-6">
                                    {pricingPlans.map((plan, index) => (
                                        <motion.div
                                            key={plan.name}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.1 }}
                                            className={`relative rounded-2xl p-6 ${
                                                plan.popular 
                                                    ? 'bg-mono-900 text-white border-2 border-mono-900' 
                                                    : 'bg-mono-50 border-2 border-mono-200'
                                            }`}
                                        >
                                            {plan.popular && (
                                                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                                                    <span className="px-3 py-1 bg-green-500 text-white text-xs font-bold rounded-full">
                                                        MOST POPULAR
                                                    </span>
                                                </div>
                                            )}

                                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                                                plan.popular ? 'bg-white/10' : 'bg-mono-200'
                                            }`}>
                                                <plan.icon className={`w-6 h-6 ${plan.popular ? 'text-white' : 'text-mono-700'}`} />
                                            </div>

                                            <h3 className={`text-xl font-bold mb-1 ${plan.popular ? 'text-white' : 'text-mono-900'}`}>
                                                {plan.name}
                                            </h3>
                                            <p className={`text-sm mb-4 ${plan.popular ? 'text-white/70' : 'text-mono-500'}`}>
                                                {plan.description}
                                            </p>

                                            <div className="mb-6">
                                                <span className={`text-4xl font-bold ${plan.popular ? 'text-white' : 'text-mono-900'}`}>
                                                    {plan.price}
                                                </span>
                                                <span className={`text-sm ${plan.popular ? 'text-white/70' : 'text-mono-500'}`}>
                                                    {plan.period}
                                                </span>
                                            </div>

                                            <ul className="space-y-3 mb-6">
                                                {plan.features.map((feature, idx) => (
                                                    <li key={idx} className="flex items-start space-x-2">
                                                        <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                                                            plan.popular ? 'text-green-400' : 'text-green-600'
                                                        }`} />
                                                        <span className={`text-sm ${plan.popular ? 'text-white/90' : 'text-mono-700'}`}>
                                                            {feature}
                                                        </span>
                                                    </li>
                                                ))}
                                            </ul>

                                            <Link
                                                href="/register"
                                                className={`block w-full py-3 px-4 rounded-xl font-medium text-center transition-all ${
                                                    plan.popular 
                                                        ? 'bg-white text-mono-900 hover:bg-mono-100' 
                                                        : 'bg-mono-900 text-white hover:bg-mono-800'
                                                }`}
                                            >
                                                {plan.cta}
                                            </Link>
                                        </motion.div>
                                    ))}
                                </div>

                                {/* Trust badges */}
                                <div className="mt-8 text-center">
                                    <p className="text-mono-500 text-sm">
                                        🔒 Secure payment with Razorpay • Cancel anytime • No hidden fees
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    )
}

export default function Home() {
    const [isPricingOpen, setIsPricingOpen] = useState(false)

    return (
        <main className="min-h-screen relative">
            {/* Fixed Background - Credit Card Shuffle Animation */}
            <CardFan3D 
                config={{
                    dealDuration: 0.7,
                    dealDelay: 0.12,
                    holdDuration: 2000,
                    arcHeight: 180,
                }}
            />

            {/* Content Layer - Above the background */}
            <div className="relative z-10">
                {/* Navigation - Glass Formula */}
                <nav className="fixed top-4 left-4 right-4 z-50 mx-auto max-w-7xl">
                    <div className="backdrop-blur-xl bg-white/80 border border-gray-200 rounded-2xl px-6 shadow-lg">
                        <div className="flex items-center justify-between h-16">
                            <div className="flex items-center space-x-2">
                                <div className="w-10 h-10 rounded-xl bg-gray-900 flex items-center justify-center">
                                    <Sparkles className="w-6 h-6 text-white" />
                                </div>
                                <span className="text-xl font-display font-bold text-gray-900 tracking-tight">FinBuddy</span>
                            </div>

                            <div className="hidden md:flex items-center space-x-8">
                                <Link href="#features" className="text-gray-600 hover:text-gray-900 transition-all duration-300 font-medium">Features</Link>
                                <Link href="#agents" className="text-gray-600 hover:text-gray-900 transition-all duration-300 font-medium">AI Agents</Link>
                                <button onClick={() => setIsPricingOpen(true)} className="text-gray-600 hover:text-gray-900 transition-all duration-300 font-medium">Pricing</button>
                            </div>

                            <div className="flex items-center space-x-4">
                                <Link href="/login" className="px-4 py-2 text-gray-600 hover:text-gray-900 font-medium transition-all">Login</Link>
                                <Link href="/register" className="px-4 py-2 bg-gray-900 text-white rounded-xl font-medium hover:bg-gray-800 transition-all">Get Started</Link>
                            </div>
                        </div>
                    </div>
                </nav>

                {/* Hero Section */}
                <section className="relative pt-36 pb-20 px-4 min-h-screen flex items-center">
                    <div className="relative max-w-7xl mx-auto text-center">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                        >
                            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-gray-100 border border-gray-200 mb-8">
                                <Sparkles className="w-4 h-4 text-gray-700" />
                                <span className="text-sm text-gray-700 font-medium">Powered by Gemini 2.5 Flash</span>
                            </div>

                            <h1 className="text-5xl md:text-7xl font-display font-bold mb-6 tracking-tight">
                                <span className="text-gray-900">Your AI-Powered</span>
                                <br />
                                <span className="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Financial Coach</span>
                            </h1>

                            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10 font-medium">
                                FinBuddy helps you track expenses, grow investments, and achieve financial freedom
                                with 13 specialized AI agents working for you 24/7.
                            </p>

                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <Link href="/register" className="px-8 py-4 bg-gray-900 text-white rounded-xl font-semibold text-lg hover:bg-gray-800 transition-all flex items-center space-x-2 shadow-xl">
                                    <span>Start Free Trial</span>
                                    <ArrowRight className="w-5 h-5" />
                                </Link>
                            </div>
                        </motion.div>

                        {/* Stats - Glass Cards */}
                        <motion.div
                            className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20"
                            initial={{ opacity: 0, y: 40 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                        >
                            {stats.map((stat, index) => (
                                <div key={index} className="backdrop-blur-xl bg-white/80 border border-gray-200 rounded-2xl p-6 shadow-lg">
                                    <div className="text-3xl font-bold text-gray-900 tracking-tight">{stat.value}</div>
                                    <div className="text-sm text-gray-500 mt-1 font-medium">{stat.label}</div>
                                </div>
                            ))}
                        </motion.div>
                    </div>
                </section>

                {/* Features Section */}
                <section id="features" className="py-20 bg-white">
                    <div className="max-w-7xl mx-auto px-4">
                        <div className="text-center mb-16">
                            <h2 className="text-4xl font-display font-bold text-gray-900 mb-4 tracking-tight">
                                Everything You Need
                            </h2>
                            <p className="text-gray-600 max-w-2xl mx-auto font-medium">
                                Comprehensive financial management powered by cutting-edge AI technology.
                            </p>
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                            {features.map((feature, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, y: 20 }}
                                    whileInView={{ opacity: 1, y: 0 }}
                                    viewport={{ once: true }}
                                    transition={{ delay: index * 0.1 }}
                                    className="bg-white border border-gray-200 rounded-2xl p-6 hover:shadow-xl hover:border-blue-200 transition-all"
                                >
                                    <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center mb-4">
                                        <feature.icon className="w-6 h-6 text-blue-600" />
                                    </div>
                                    <h3 className="text-lg font-bold text-gray-900 mb-2">{feature.title}</h3>
                                    <p className="text-gray-600 text-sm">{feature.description}</p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* AI Agents Section */}
                <section id="agents" className="py-20 px-4 bg-slate-100">
                    <div className="max-w-7xl mx-auto">
                        <div className="text-center mb-16">
                            <h2 className="text-4xl font-display font-bold text-gray-900 mb-4 tracking-tight">
                                13 Specialized AI Agents
                            </h2>
                            <p className="text-gray-600 max-w-2xl mx-auto font-medium">
                                Each agent is trained to excel in specific financial domains.
                            </p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8">
                            {/* Block 1 */}
                            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                                <div className="flex items-center space-x-3 mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center">
                                        <PiggyBank className="w-5 h-5 text-blue-600" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900 tracking-tight">Money Management</h3>
                                </div>
                                <ul className="space-y-2 text-sm text-gray-600">
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>OCR Agent - Extract from SMS/receipts</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>Watchdog Agent - Anomaly detection</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>Categorize Agent - Smart classification</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>Investment Detector - Find patterns</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>Money Growth Agent - Budget advice</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span><span>News Agent - Personal finance updates</span></li>
                                </ul>
                            </div>

                            {/* Block 2 */}
                            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                                <div className="flex items-center space-x-3 mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center">
                                        <TrendingUp className="w-5 h-5 text-green-600" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900 tracking-tight">Investment</h3>
                                </div>
                                <ul className="space-y-2 text-sm text-gray-600">
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span><span>Analysis Agent - Risk profiling</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span><span>Stock Agent - Equity research</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span><span>Investment Agent - Portfolio planning</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span><span>Market News Agent - Real-time updates</span></li>
                                </ul>
                            </div>

                            {/* Block 3 */}
                            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
                                <div className="flex items-center space-x-3 mb-4">
                                    <div className="w-10 h-10 rounded-xl bg-purple-100 flex items-center justify-center">
                                        <CreditCard className="w-5 h-5 text-purple-600" />
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900 tracking-tight">Financial Products</h3>
                                </div>
                                <ul className="space-y-2 text-sm text-gray-600">
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span><span>Credit Card Agent - Best card matching</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span><span>ITR Agent - Tax optimization</span></li>
                                    <li className="flex items-center space-x-2"><span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span><span>Loan Agent - EMI & eligibility</span></li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>

                {/* CTA Section */}
                <section className="py-20 px-4 bg-white">
                    <div className="max-w-4xl mx-auto text-center">
                        <motion.div
                            className="bg-gray-900 rounded-3xl p-12 shadow-2xl"
                            initial={{ opacity: 0, scale: 0.95 }}
                            whileInView={{ opacity: 1, scale: 1 }}
                            transition={{ duration: 0.5 }}
                            viewport={{ once: true }}
                        >
                            <h2 className="text-3xl md:text-4xl font-display font-bold text-white mb-4 tracking-tight">
                                Ready to Transform Your Finances?
                            </h2>
                            <p className="text-white/80 mb-8 font-medium">
                                Join thousands of users who are already achieving their financial goals with FinBuddy.
                            </p>
                            <Link href="/register" className="inline-flex items-center space-x-2 px-8 py-4 bg-white text-gray-900 font-semibold rounded-xl hover:bg-gray-100 transition-all shadow-xl">
                                <span>Get Started Free</span>
                                <ArrowRight className="w-5 h-5" />
                            </Link>
                        </motion.div>
                    </div>
                </section>

                {/* Footer */}
                <footer className="border-t border-gray-200 py-12 px-4 bg-slate-50">
                    <div className="max-w-7xl mx-auto">
                        <div className="flex flex-col md:flex-row items-center justify-between">
                            <div className="flex items-center space-x-2 mb-4 md:mb-0">
                                <div className="w-8 h-8 rounded-xl bg-gray-900 flex items-center justify-center">
                                    <Sparkles className="w-4 h-4 text-white" />
                                </div>
                                <span className="text-lg font-display font-bold text-gray-900 tracking-tight">FinBuddy</span>
                            </div>
                            <p className="text-sm text-gray-500 font-medium">
                                © 2026 FinBuddy. All rights reserved.
                            </p>
                        </div>
                    </div>
                </footer>
            </div>

            {/* Pricing Modal */}
            <PricingModal isOpen={isPricingOpen} onClose={() => setIsPricingOpen(false)} />
        </main>
    )
}
