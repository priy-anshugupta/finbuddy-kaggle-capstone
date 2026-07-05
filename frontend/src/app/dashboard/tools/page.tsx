'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Calculator,
    CreditCard,
    FileText,
    Home,
    GraduationCap,
    Car,
    PieChart,
    DollarSign,
    Briefcase,
    TrendingUp,
    X,
    ArrowRight,
    Info,
    CheckCircle,
    AlertCircle,
    Search,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { api } from '@/lib/api'

// Type definitions
interface Tool {
    id: string
    name: string
    desc: string
    icon: any
    color: string
    category: string
}

// Utility function for formatting
const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
    }).format(amount)
}

// Tax Calculator Component
function TaxCalculator({ onClose }: { onClose: () => void }) {
    const [income, setIncome] = useState<number>(1000000)
    const [deductions80C, setDeductions80C] = useState<number>(150000)
    const [deductions80D, setDeductions80D] = useState<number>(25000)
    const [hra, setHra] = useState<number>(0)
    const [otherDeductions, setOtherDeductions] = useState<number>(0)

    const calculateTax = () => {
        // Old Regime Tax Calculation
        const oldTaxableIncome = Math.max(0, income - deductions80C - deductions80D - hra - otherDeductions - 50000)
        let oldTax = 0
        if (oldTaxableIncome > 1500000) {
            oldTax = 187500 + (oldTaxableIncome - 1500000) * 0.30
        } else if (oldTaxableIncome > 1250000) {
            oldTax = 125000 + (oldTaxableIncome - 1250000) * 0.25
        } else if (oldTaxableIncome > 1000000) {
            oldTax = 100000 + (oldTaxableIncome - 1000000) * 0.20
        } else if (oldTaxableIncome > 500000) {
            oldTax = (oldTaxableIncome - 500000) * 0.20
        } else if (oldTaxableIncome > 250000) {
            oldTax = (oldTaxableIncome - 250000) * 0.05
        }
        oldTax = oldTax + oldTax * 0.04

        // New Regime Tax Calculation
        const newTaxableIncome = Math.max(0, income - 75000)
        let newTax = 0
        if (newTaxableIncome > 1500000) {
            newTax = 150000 + (newTaxableIncome - 1500000) * 0.30
        } else if (newTaxableIncome > 1200000) {
            newTax = 90000 + (newTaxableIncome - 1200000) * 0.20
        } else if (newTaxableIncome > 900000) {
            newTax = 45000 + (newTaxableIncome - 900000) * 0.15
        } else if (newTaxableIncome > 600000) {
            newTax = 15000 + (newTaxableIncome - 600000) * 0.10
        } else if (newTaxableIncome > 300000) {
            newTax = (newTaxableIncome - 300000) * 0.05
        }
        newTax = newTax + newTax * 0.04

        return { oldTax: Math.round(oldTax), newTax: Math.round(newTax), savings: Math.round(Math.abs(oldTax - newTax)) }
    }

    const { oldTax, newTax, savings } = calculateTax()
    const betterRegime = oldTax < newTax ? 'old' : 'new'

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Annual Income (₹)</label>
                    <input
                        type="number"
                        value={income}
                        onChange={(e) => setIncome(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400"
                    />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">80C Deductions (Max ₹1.5L)</label>
                    <input
                        type="number"
                        value={deductions80C}
                        onChange={(e) => setDeductions80C(Math.min(150000, Number(e.target.value)))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400"
                    />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">80D Health Insurance (Max ₹75K)</label>
                    <input
                        type="number"
                        value={deductions80D}
                        onChange={(e) => setDeductions80D(Math.min(75000, Number(e.target.value)))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400"
                    />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">HRA Exemption (₹)</label>
                    <input
                        type="number"
                        value={hra}
                        onChange={(e) => setHra(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400"
                    />
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
                <div className={`p-4 rounded-xl border-2 ${betterRegime === 'old' ? 'border-green-500 bg-green-50' : 'border-mono-300 bg-mono-100'}`}>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-mono-700 font-medium">Old Regime</span>
                        {betterRegime === 'old' && <CheckCircle className="w-5 h-5 text-green-600" />}
                    </div>
                    <p className="text-2xl font-bold text-mono-900">{formatCurrency(oldTax)}</p>
                    <p className="text-xs text-mono-500">After all deductions</p>
                </div>
                <div className={`p-4 rounded-xl border-2 ${betterRegime === 'new' ? 'border-green-500 bg-green-50' : 'border-mono-300 bg-mono-100'}`}>
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-mono-700 font-medium">New Regime</span>
                        {betterRegime === 'new' && <CheckCircle className="w-5 h-5 text-green-600" />}
                    </div>
                    <p className="text-2xl font-bold text-mono-900">{formatCurrency(newTax)}</p>
                    <p className="text-xs text-mono-500">Limited deductions</p>
                </div>
            </div>

            <div className="p-4 bg-mono-900 rounded-xl">
                <div className="flex items-center space-x-2 mb-2">
                    <Info className="w-5 h-5 text-white" />
                    <span className="font-semibold text-white">Recommendation</span>
                </div>
                <p className="text-mono-300">
                    Based on your inputs, the <span className="text-green-400 font-bold">{betterRegime === 'old' ? 'Old Regime' : 'New Regime'}</span> is 
                    better for you. You can save <span className="text-green-400 font-bold">{formatCurrency(savings)}</span> annually!
                </p>
            </div>
        </div>
    )
}

// EMI Calculator Component
function EMICalculator({ onClose }: { onClose: () => void }) {
    const [loanAmount, setLoanAmount] = useState<number>(5000000)
    const [interestRate, setInterestRate] = useState<number>(8.5)
    const [tenure, setTenure] = useState<number>(20)
    const [prepayment, setPrepayment] = useState<number>(0)

    const calculateEMI = () => {
        const principal = loanAmount - prepayment
        const monthlyRate = interestRate / 12 / 100
        const months = tenure * 12

        if (monthlyRate === 0) {
            return { emi: principal / months, totalPayment: principal, totalInterest: 0, principal }
        }

        const emi = principal * monthlyRate * Math.pow(1 + monthlyRate, months) / (Math.pow(1 + monthlyRate, months) - 1)
        const totalPayment = emi * months
        const totalInterest = totalPayment - principal

        return { emi: Math.round(emi), totalPayment: Math.round(totalPayment), totalInterest: Math.round(totalInterest), principal }
    }

    const { emi, totalPayment, totalInterest, principal } = calculateEMI()
    const interestPercentage = (totalInterest / (totalPayment || 1)) * 100

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Loan Amount (₹)</label>
                    <input type="number" value={loanAmount} onChange={(e) => setLoanAmount(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                    <div className="flex gap-2 mt-2">
                        {[1000000, 2500000, 5000000, 10000000].map((amt) => (
                            <button key={amt} onClick={() => setLoanAmount(amt)}
                                className={`text-xs px-2 py-1 rounded ${loanAmount === amt ? 'bg-green-600 text-white' : 'bg-mono-200 text-mono-700'}`}>
                                {amt >= 10000000 ? '1Cr' : `${amt / 100000}L`}
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Interest Rate (%): {interestRate}%</label>
                    <input type="range" min="5" max="18" step="0.1" value={interestRate}
                        onChange={(e) => setInterestRate(Number(e.target.value))} className="w-full accent-green-600" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Loan Tenure: {tenure} Years</label>
                    <input type="range" min="1" max="30" value={tenure}
                        onChange={(e) => setTenure(Number(e.target.value))} className="w-full accent-green-600" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Prepayment Amount (₹)</label>
                    <input type="number" value={prepayment} onChange={(e) => setPrepayment(Math.min(loanAmount, Number(e.target.value)))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500 uppercase">Monthly EMI</p>
                    <p className="text-2xl font-bold text-green-600">{formatCurrency(emi)}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500 uppercase">Total Interest</p>
                    <p className="text-2xl font-bold text-orange-600">{formatCurrency(totalInterest)}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500 uppercase">Total Payment</p>
                    <p className="text-2xl font-bold text-mono-900">{formatCurrency(totalPayment)}</p>
                </div>
            </div>

            <div className="space-y-2">
                <div className="flex justify-between text-sm">
                    <span className="text-mono-600">Principal vs Interest</span>
                    <span className="text-mono-600">{(100 - interestPercentage).toFixed(1)}% : {interestPercentage.toFixed(1)}%</span>
                </div>
                <div className="h-4 bg-mono-200 rounded-full overflow-hidden flex">
                    <div className="bg-green-500 h-full transition-all duration-300" style={{ width: `${100 - interestPercentage}%` }} />
                    <div className="bg-orange-500 h-full transition-all duration-300" style={{ width: `${interestPercentage}%` }} />
                </div>
            </div>
        </div>
    )
}

// SIP Calculator Component
function SIPCalculator({ onClose }: { onClose: () => void }) {
    const [monthlyInvestment, setMonthlyInvestment] = useState<number>(10000)
    const [expectedReturn, setExpectedReturn] = useState<number>(12)
    const [years, setYears] = useState<number>(10)
    const [goalAmount, setGoalAmount] = useState<number>(0)

    const calculateSIP = () => {
        const monthlyRate = expectedReturn / 12 / 100
        const months = years * 12
        const fv = monthlyInvestment * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate)
        const totalInvested = monthlyInvestment * months
        const wealthGained = fv - totalInvested
        let requiredSIP = 0
        if (goalAmount > 0) {
            requiredSIP = goalAmount / (((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate))
        }
        return { futureValue: Math.round(fv), totalInvested: Math.round(totalInvested), wealthGained: Math.round(wealthGained), requiredSIP: Math.round(requiredSIP) }
    }

    const { futureValue, totalInvested, wealthGained, requiredSIP } = calculateSIP()

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Monthly SIP Amount (₹)</label>
                    <input type="number" value={monthlyInvestment} onChange={(e) => setMonthlyInvestment(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                    <div className="flex gap-2 mt-2">
                        {[5000, 10000, 25000, 50000].map((amt) => (
                            <button key={amt} onClick={() => setMonthlyInvestment(amt)}
                                className={`text-xs px-2 py-1 rounded ${monthlyInvestment === amt ? 'bg-emerald-600 text-white' : 'bg-mono-200 text-mono-700'}`}>
                                {amt >= 1000 ? `${amt / 1000}K` : amt}
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Expected Return: {expectedReturn}% p.a.</label>
                    <input type="range" min="6" max="20" step="0.5" value={expectedReturn}
                        onChange={(e) => setExpectedReturn(Number(e.target.value))} className="w-full accent-emerald-600" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Investment Period: {years} Years</label>
                    <input type="range" min="1" max="40" value={years}
                        onChange={(e) => setYears(Number(e.target.value))} className="w-full accent-emerald-600" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Target Goal Amount (Optional)</label>
                    <input type="number" value={goalAmount} onChange={(e) => setGoalAmount(Number(e.target.value))}
                        placeholder="Enter your target corpus" className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500 uppercase">Total Invested</p>
                    <p className="text-2xl font-bold text-mono-900">{formatCurrency(totalInvested)}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500 uppercase">Wealth Gained</p>
                    <p className="text-2xl font-bold text-green-600">+{formatCurrency(wealthGained)}</p>
                </div>
                <div className="p-4 bg-emerald-50 rounded-xl text-center border-2 border-emerald-500">
                    <p className="text-xs text-mono-500 uppercase">Future Value</p>
                    <p className="text-2xl font-bold text-emerald-600">{formatCurrency(futureValue)}</p>
                </div>
            </div>

            {goalAmount > 0 && (
                <div className="p-4 bg-mono-900 rounded-xl">
                    <div className="flex items-center space-x-2 mb-2">
                        <TrendingUp className="w-5 h-5 text-white" />
                        <span className="font-semibold text-white">Goal Planning</span>
                    </div>
                    <p className="text-mono-300">
                        To reach your goal of <span className="text-emerald-400 font-bold">{formatCurrency(goalAmount)}</span> in {years} years,
                        you need to invest <span className="text-emerald-400 font-bold">{formatCurrency(requiredSIP)}</span> monthly.
                    </p>
                </div>
            )}

            <div className="space-y-2">
                <p className="text-sm text-mono-600">Investment Growth Over Time</p>
                <div className="h-20 flex items-end gap-1">
                    {Array.from({ length: Math.min(years, 20) }, (_, i) => {
                        const yr = i + 1
                        const monthlyRate = expectedReturn / 12 / 100
                        const months = yr * 12
                        const fv = monthlyInvestment * ((Math.pow(1 + monthlyRate, months) - 1) / monthlyRate) * (1 + monthlyRate)
                        const height = (fv / futureValue) * 100
                        return <div key={yr} className="flex-1 bg-emerald-500 rounded-t transition-all duration-300 hover:bg-emerald-400" style={{ height: `${height}%` }} title={`Year ${yr}: ${formatCurrency(fv)}`} />
                    })}
                </div>
            </div>
        </div>
    )
}

// Home Loan Eligibility Calculator
function HomeLoanCalculator({ onClose }: { onClose: () => void }) {
    const [monthlyIncome, setMonthlyIncome] = useState<number>(100000)
    const [existingEMI, setExistingEMI] = useState<number>(0)
    const [interestRate, setInterestRate] = useState<number>(8.5)
    const [tenure, setTenure] = useState<number>(20)

    const calculateEligibility = () => {
        const maxEMI = (monthlyIncome * 0.5) - existingEMI
        const monthlyRate = interestRate / 12 / 100
        const months = tenure * 12
        const eligibleAmount = maxEMI * (Math.pow(1 + monthlyRate, months) - 1) / (monthlyRate * Math.pow(1 + monthlyRate, months))
        return { maxEMI: Math.max(0, Math.round(maxEMI)), eligibleAmount: Math.max(0, Math.round(eligibleAmount)), dti: ((existingEMI / monthlyIncome) * 100).toFixed(1) }
    }

    const { maxEMI, eligibleAmount, dti } = calculateEligibility()

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Monthly Income (₹)</label>
                    <input type="number" value={monthlyIncome} onChange={(e) => setMonthlyIncome(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Existing EMIs (₹)</label>
                    <input type="number" value={existingEMI} onChange={(e) => setExistingEMI(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Interest Rate: {interestRate}%</label>
                    <input type="range" min="6" max="12" step="0.1" value={interestRate}
                        onChange={(e) => setInterestRate(Number(e.target.value))} className="w-full accent-orange-500" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Loan Tenure: {tenure} Years</label>
                    <input type="range" min="5" max="30" value={tenure}
                        onChange={(e) => setTenure(Number(e.target.value))} className="w-full accent-orange-500" />
                </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
                <div className="p-6 bg-orange-50 rounded-xl border-2 border-orange-500 text-center">
                    <Home className="w-8 h-8 text-orange-600 mx-auto mb-2" />
                    <p className="text-xs text-mono-500 uppercase mb-1">Eligible Loan Amount</p>
                    <p className="text-3xl font-bold text-orange-600">{formatCurrency(eligibleAmount)}</p>
                </div>
                <div className="p-6 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <Calculator className="w-8 h-8 text-mono-500 mx-auto mb-2" />
                    <p className="text-xs text-mono-500 uppercase mb-1">Maximum EMI Capacity</p>
                    <p className="text-3xl font-bold text-mono-900">{formatCurrency(maxEMI)}</p>
                </div>
            </div>

            <div className={`p-4 rounded-xl border-2 ${Number(dti) > 40 ? 'bg-red-50 border-red-500' : 'bg-green-50 border-green-500'}`}>
                <div className="flex items-center space-x-2 mb-2">
                    {Number(dti) > 40 ? <AlertCircle className="w-5 h-5 text-red-600" /> : <CheckCircle className="w-5 h-5 text-green-600" />}
                    <span className="font-semibold text-mono-900">Debt-to-Income Ratio: {dti}%</span>
                </div>
                <p className="text-mono-700 text-sm">
                    {Number(dti) > 40 ? 'Your current EMI burden is high. Consider reducing existing debts before applying for a home loan.' : 'Your debt-to-income ratio is healthy. You have good chances of loan approval!'}
                </p>
            </div>
        </div>
    )
}

// Credit Card Matcher Component
function CreditCardMatcher({ onClose }: { onClose: () => void }) {
    const [spendingCategory, setSpendingCategory] = useState<string>('general')
    const [monthlySpending, setMonthlySpending] = useState<number>(50000)
    const [annualIncome, setAnnualIncome] = useState<number>(1000000)
    const [isLoading, setIsLoading] = useState<boolean>(false)
    const [creditCards, setCreditCards] = useState<any[]>([])
    const [selectedCard, setSelectedCard] = useState<any | null>(null)
    const [hasSearched, setHasSearched] = useState<boolean>(false)

    const searchCreditCards = async () => {
        setIsLoading(true)
        setHasSearched(true)
        try {
            const response = await api.post('/credit-cards/recommendations', {
                spending_category: spendingCategory,
                monthly_spending: monthlySpending,
                annual_income: annualIncome,
                country: 'India',
                max_results: 8
            })
            setCreditCards(response.data.cards || [])
        } catch (error) {
            console.error('Error fetching credit cards:', error)
            // Fallback to static data if API fails
            setCreditCards([
                { id: 'hdfc-regalia', name: 'HDFC Regalia', issuer: 'HDFC Bank', annual_fee: '₹2,500', best_for: ['travel', 'premium'], rewards_summary: '4X reward points on travel & dining', key_benefits: ['Complimentary airport lounge access', 'Golf privileges', 'Travel insurance up to ₹1 Cr', 'Milestone benefits'], eligibility: 'Annual income ≥ ₹12 Lakhs' },
                { id: 'sbi-simplyclick', name: 'SBI SimplyCLICK', issuer: 'SBI Card', annual_fee: '₹499', best_for: ['online', 'shopping'], rewards_summary: '10X rewards on partner sites', key_benefits: ['10X on Amazon, Cleartrip, etc.', '5X on other online spends', 'Welcome gift ₹500 Amazon voucher', 'No annual fee on ₹1L spend'], eligibility: 'Annual income ≥ ₹3 Lakhs' },
                { id: 'icici-amazon-pay', name: 'Amazon Pay ICICI', issuer: 'ICICI Bank', annual_fee: 'FREE', best_for: ['shopping', 'amazon'], rewards_summary: '5% cashback on Amazon for Prime', key_benefits: ['5% on Amazon (Prime members)', '2% on paying via Amazon Pay', '1% on other spends', 'No joining/annual fee'], eligibility: 'Annual income ≥ ₹3 Lakhs' },
                { id: 'axis-flipkart', name: 'Axis Flipkart', issuer: 'Axis Bank', annual_fee: '₹500', best_for: ['shopping', 'flipkart'], rewards_summary: '5% cashback on Flipkart', key_benefits: ['5% unlimited cashback on Flipkart', '4% on Myntra, 2Up, Cleartrip', '1.5% on all other spends', 'No annual fee on ₹2L spend'], eligibility: 'Annual income ≥ ₹3 Lakhs' },
                { id: 'hdfc-millennia', name: 'HDFC Millennia', issuer: 'HDFC Bank', annual_fee: '₹1,000', best_for: ['general', 'online'], rewards_summary: '5% cashback on online shopping', key_benefits: ['5% on Amazon, Flipkart, etc.', '2.5% on all other online spends', '1% on offline spends', 'PayBack points integration'], eligibility: 'Annual income ≥ ₹5 Lakhs' },
            ])
        } finally {
            setIsLoading(false)
        }
    }

    const potentialCashback = (monthlySpending * 0.025 * 12)

    return (
        <div className="space-y-6">
            {/* Card Detail Modal */}
            {selectedCard && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setSelectedCard(null)}>
                    <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6 border-b border-mono-200">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-700 rounded-xl flex items-center justify-center">
                                        <CreditCard className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-xl font-bold text-mono-900">{selectedCard.name}</h3>
                                        <p className="text-sm text-mono-500">{selectedCard.issuer || 'Credit Card'}</p>
                                    </div>
                                </div>
                                <button onClick={() => setSelectedCard(null)} className="p-2 hover:bg-mono-100 rounded-lg">
                                    <X className="w-5 h-5 text-mono-500" />
                                </button>
                            </div>
                        </div>
                        <div className="p-6 space-y-5">
                            {/* Fees Section */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-mono-50 rounded-xl">
                                    <p className="text-xs text-mono-500 uppercase mb-1">Annual Fee</p>
                                    <p className="text-lg font-bold text-mono-900">{selectedCard.annual_fee || 'N/A'}</p>
                                </div>
                                <div className="p-4 bg-mono-50 rounded-xl">
                                    <p className="text-xs text-mono-500 uppercase mb-1">Joining Fee</p>
                                    <p className="text-lg font-bold text-mono-900">{selectedCard.joining_fee || selectedCard.annual_fee || 'N/A'}</p>
                                </div>
                            </div>

                            {/* Rewards Summary */}
                            {selectedCard.rewards_summary && (
                                <div className="p-4 bg-purple-50 rounded-xl border border-purple-200">
                                    <p className="text-xs text-purple-600 uppercase mb-1 font-semibold">Rewards</p>
                                    <p className="text-mono-800">{selectedCard.rewards_summary}</p>
                                </div>
                            )}

                            {/* Best For Tags */}
                            {selectedCard.best_for && selectedCard.best_for.length > 0 && (
                                <div>
                                    <p className="text-xs text-mono-500 uppercase mb-2">Best For</p>
                                    <div className="flex flex-wrap gap-2">
                                        {selectedCard.best_for.map((tag: string, idx: number) => (
                                            <span key={idx} className="px-3 py-1 bg-mono-100 text-mono-700 rounded-full text-sm capitalize">
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Key Benefits */}
                            {selectedCard.key_benefits && selectedCard.key_benefits.length > 0 && (
                                <div>
                                    <p className="text-xs text-mono-500 uppercase mb-2">Key Benefits</p>
                                    <ul className="space-y-2">
                                        {selectedCard.key_benefits.map((benefit: string, idx: number) => (
                                            <li key={idx} className="flex items-start space-x-2">
                                                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                                                <span className="text-mono-700 text-sm">{benefit}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}

                            {/* Eligibility */}
                            {selectedCard.eligibility && (
                                <div className="p-4 bg-mono-900 rounded-xl">
                                    <p className="text-xs text-mono-400 uppercase mb-1">Eligibility</p>
                                    <p className="text-white">{selectedCard.eligibility}</p>
                                </div>
                            )}

                            {/* Sources */}
                            {selectedCard.sources && selectedCard.sources.length > 0 && (
                                <div>
                                    <p className="text-xs text-mono-500 uppercase mb-2">Sources</p>
                                    <div className="space-y-1">
                                        {selectedCard.sources.map((url: string, idx: number) => (
                                            <a key={idx} href={url} target="_blank" rel="noopener noreferrer" className="block text-sm text-purple-600 hover:underline truncate">
                                                {url}
                                            </a>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Apply Button */}
                            {selectedCard.apply_url && (
                                <a href={selectedCard.apply_url} target="_blank" rel="noopener noreferrer" className="block w-full py-3 bg-purple-600 hover:bg-purple-700 text-white text-center rounded-xl font-semibold transition-colors">
                                    Apply Now
                                </a>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="grid md:grid-cols-3 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Primary Spending</label>
                    <select value={spendingCategory} onChange={(e) => setSpendingCategory(e.target.value)}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400">
                        <option value="general">General</option>
                        <option value="travel">Travel</option>
                        <option value="shopping">Shopping</option>
                        <option value="dining">Dining</option>
                        <option value="online">Online</option>
                        <option value="utility">Bills & Utilities</option>
                        <option value="fuel">Fuel</option>
                        <option value="premium">Premium/Lifestyle</option>
                    </select>
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Monthly Spending (₹)</label>
                    <input type="number" value={monthlySpending} onChange={(e) => setMonthlySpending(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Annual Income (₹)</label>
                    <input type="number" value={annualIncome} onChange={(e) => setAnnualIncome(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
            </div>

            {/* Search Button */}
            <button 
                onClick={searchCreditCards} 
                disabled={isLoading}
                className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white rounded-xl font-semibold transition-colors flex items-center justify-center space-x-2"
            >
                {isLoading ? (
                    <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>Searching with AI...</span>
                    </>
                ) : (
                    <>
                        <Search className="w-5 h-5" />
                        <span>Find Best Credit Cards</span>
                    </>
                )}
            </button>

            <div className="p-4 bg-purple-50 rounded-xl border-2 border-purple-500">
                <p className="text-mono-700">Potential Annual Savings: <span className="text-purple-600 font-bold">{formatCurrency(potentialCashback)}</span> with the right credit card!</p>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto">
                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="w-12 h-12 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4" />
                        <p className="text-mono-600">AI is searching for the best credit cards...</p>
                        <p className="text-xs text-mono-400 mt-1">This may take a few seconds</p>
                    </div>
                ) : creditCards.length > 0 ? (
                    creditCards.map((card, idx) => (
                        <div 
                            key={card.id || idx} 
                            onClick={() => setSelectedCard(card)}
                            className="p-4 bg-mono-100 rounded-xl border border-mono-200 hover:border-purple-400 hover:shadow-md transition-all cursor-pointer"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-3">
                                    <CreditCard className="w-6 h-6 text-purple-600" />
                                    <div>
                                        <h4 className="font-semibold text-mono-900">{card.name}</h4>
                                        <p className="text-xs text-mono-500">{card.issuer || 'Credit Card'}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-purple-600 font-bold text-sm">{card.annual_fee || 'Check fee'}</p>
                                    <p className="text-xs text-mono-500">Annual Fee</p>
                                </div>
                            </div>
                            {card.rewards_summary && (
                                <p className="text-sm text-mono-600 mt-2 line-clamp-2">{card.rewards_summary}</p>
                            )}
                            <div className="flex items-center justify-between mt-3">
                                <div className="flex flex-wrap gap-1">
                                    {(card.best_for || []).slice(0, 3).map((tag: string, i: number) => (
                                        <span key={i} className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs capitalize">{tag}</span>
                                    ))}
                                </div>
                                <span className="text-xs text-purple-600 font-medium">View Details →</span>
                            </div>
                        </div>
                    ))
                ) : hasSearched ? (
                    <div className="text-center py-8 text-mono-500">
                        <CreditCard className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No cards found. Try adjusting your criteria.</p>
                    </div>
                ) : (
                    <div className="text-center py-8 text-mono-500">
                        <Search className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>Click "Find Best Credit Cards" to search using AI</p>
                    </div>
                )}
            </div>
        </div>
    )
}

// Education Loan Calculator
function EducationLoanCalculator({ onClose }: { onClose: () => void }) {
    const [courseFee, setCourseFee] = useState<number>(2000000)
    const [livingExpenses, setLivingExpenses] = useState<number>(500000)
    const [interestRate, setInterestRate] = useState<number>(9.5)
    const [moratoriumYears, setMoratoriumYears] = useState<number>(4)
    const [repaymentYears, setRepaymentYears] = useState<number>(10)

    const totalLoan = courseFee + livingExpenses
    const moratoriumInterest = totalLoan * (interestRate / 100) * moratoriumYears
    const principalAfterMoratorium = totalLoan + moratoriumInterest
    const monthlyRate = interestRate / 12 / 100
    const months = repaymentYears * 12
    const emi = principalAfterMoratorium * monthlyRate * Math.pow(1 + monthlyRate, months) / (Math.pow(1 + monthlyRate, months) - 1)
    const totalRepayment = emi * months

    return (
        <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Course/Tuition Fees (₹)</label>
                    <input type="number" value={courseFee} onChange={(e) => setCourseFee(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Living Expenses (₹)</label>
                    <input type="number" value={livingExpenses} onChange={(e) => setLivingExpenses(Number(e.target.value))}
                        className="w-full bg-mono-100 border border-mono-300 rounded-lg px-4 py-2.5 text-mono-900 focus:outline-none focus:ring-2 focus:ring-mono-400" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Interest Rate: {interestRate}%</label>
                    <input type="range" min="7" max="14" step="0.1" value={interestRate}
                        onChange={(e) => setInterestRate(Number(e.target.value))} className="w-full accent-indigo-600" />
                </div>
                <div>
                    <label className="text-sm text-mono-600 mb-1 block">Course Duration (Moratorium): {moratoriumYears} Years</label>
                    <input type="range" min="1" max="6" value={moratoriumYears}
                        onChange={(e) => setMoratoriumYears(Number(e.target.value))} className="w-full accent-indigo-600" />
                </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500">Total Loan</p>
                    <p className="text-xl font-bold text-mono-900">{formatCurrency(totalLoan)}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500">Moratorium Interest</p>
                    <p className="text-xl font-bold text-orange-600">{formatCurrency(Math.round(moratoriumInterest))}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500">Monthly EMI</p>
                    <p className="text-xl font-bold text-indigo-600">{formatCurrency(Math.round(emi))}</p>
                </div>
                <div className="p-4 bg-mono-100 rounded-xl text-center border border-mono-200">
                    <p className="text-xs text-mono-500">Total Repayment</p>
                    <p className="text-xl font-bold text-mono-900">{formatCurrency(Math.round(totalRepayment))}</p>
                </div>
            </div>

            <div className="p-4 bg-mono-900 rounded-xl">
                <div className="flex items-center space-x-2 mb-2">
                    <GraduationCap className="w-5 h-5 text-white" />
                    <span className="font-semibold text-white">Tax Benefit (Section 80E)</span>
                </div>
                <p className="text-mono-300 text-sm">
                    You can claim tax deduction on the entire interest paid (no upper limit) for up to 8 years from the start of repayment.
                    Potential tax savings: <span className="text-indigo-400 font-bold">{formatCurrency(Math.round((totalRepayment - principalAfterMoratorium) * 0.3))}</span> (at 30% tax bracket)
                </p>
            </div>
        </div>
    )
}

// Tool Modal Component
function ToolModal({ tool, isOpen, onClose }: { tool: Tool | null; isOpen: boolean; onClose: () => void }) {
    if (!tool) return null

    const getCalculatorComponent = () => {
        switch (tool.id) {
            case 'tax-calc': return <TaxCalculator onClose={onClose} />
            case 'emi-calc': return <EMICalculator onClose={onClose} />
            case 'sip-calc': return <SIPCalculator onClose={onClose} />
            case 'home-loan': return <HomeLoanCalculator onClose={onClose} />
            case 'cc-finder': return <CreditCardMatcher onClose={onClose} />
            case 'education': return <EducationLoanCalculator onClose={onClose} />
            default: return <p className="text-slate-400">Calculator coming soon...</p>
        }
    }

    const colorMap: Record<string, string> = {
        blue: 'from-blue-600 to-blue-800', purple: 'from-purple-600 to-purple-800',
        green: 'from-green-600 to-green-800', orange: 'from-orange-600 to-orange-800',
        emerald: 'from-emerald-600 to-emerald-800', indigo: 'from-indigo-600 to-indigo-800',
    }

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-[100]" onClick={onClose} />
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 pointer-events-none">
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }} 
                            animate={{ opacity: 1, scale: 1 }} 
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="w-full max-w-2xl max-h-[85vh] overflow-y-auto bg-white rounded-[24px] shadow-2xl border border-mono-200 pointer-events-auto"
                        >
                            <div className="sticky top-0 p-5 border-b border-mono-200 bg-white/95 backdrop-blur-sm rounded-t-[24px]">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center space-x-3">
                                        <div className={`p-2.5 rounded-xl bg-${tool.color}-500/20`}>
                                            <tool.icon className={`w-5 h-5 text-${tool.color}-600`} />
                                        </div>
                                        <div>
                                            <h2 className="text-lg font-bold text-mono-900">{tool.name}</h2>
                                            <p className="text-sm text-mono-500">{tool.desc}</p>
                                        </div>
                                    </div>
                                    <button onClick={onClose} className="p-2 hover:bg-mono-200 rounded-lg transition-colors">
                                        <X className="w-5 h-5 text-mono-600" />
                                    </button>
                                </div>
                            </div>
                            <div className="p-5">{getCalculatorComponent()}</div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    )
}

export default function ToolsPage() {
    const [activeCategory, setActiveCategory] = useState<'all' | 'tax' | 'loans' | 'planning'>('all')
    const [selectedTool, setSelectedTool] = useState<Tool | null>(null)
    const [isModalOpen, setIsModalOpen] = useState(false)

    const tools: Tool[] = [
        { id: 'tax-calc', name: 'Tax Regime Optimizer', desc: 'Compare Old vs New Tax Regime to find maximum savings.', icon: FileText, color: 'blue', category: 'tax' },
        { id: 'cc-finder', name: 'Credit Card Matcher', desc: 'Find the perfect card based on your spending habits.', icon: CreditCard, color: 'purple', category: 'planning' },
        { id: 'emi-calc', name: 'Smart EMI Planner', desc: 'Calculate loan EMIs with prepayment strategies.', icon: Calculator, color: 'green', category: 'loans' },
        { id: 'home-loan', name: 'Home Loan Eligibility', desc: 'Check how much loan you can get based on income.', icon: Home, color: 'orange', category: 'loans' },
        { id: 'sip-calc', name: 'SIP Goal Planner', desc: 'Plan your investments to reach financial goals.', icon: TrendingUp, color: 'emerald', category: 'planning' },
        { id: 'education', name: 'Education Loan Assistant', desc: 'Find best interest rates for higher studies.', icon: GraduationCap, color: 'indigo', category: 'loans' },
    ]

    const filteredTools = activeCategory === 'all' ? tools : tools.filter(t => t.category === activeCategory)

    const handleToolClick = (tool: Tool) => { setSelectedTool(tool); setIsModalOpen(true) }

    return (
        <DashboardLayout>
            <div className="space-y-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-mono-900">Financial Toolkit</h1>
                        <p className="text-mono-500">Calculators and utilities to optimize your finances</p>
                    </div>
                    <div className="flex space-x-2 bg-mono-200 p-1 rounded-lg border border-mono-300">
                        {['all', 'tax', 'loans', 'planning'].map((cat) => (
                            <button key={cat} onClick={() => setActiveCategory(cat as any)}
                                className={`px-4 py-1.5 rounded-md text-xs font-medium capitalize transition-all ${activeCategory === cat ? 'bg-mono-900 text-white shadow-sm' : 'text-mono-600 hover:text-mono-900'}`}>
                                {cat}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredTools.map((tool, idx) => (
                        <motion.div key={tool.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: idx * 0.05 }}
                            className="glass-card p-6 hover:border-mono-400 transition-all cursor-pointer group relative overflow-hidden"
                            onClick={() => handleToolClick(tool)}>
                            <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
                                <tool.icon className={`w-24 h-24 text-${tool.color}-500`} />
                            </div>
                            <div className="relative z-10">
                                <div className={`w-12 h-12 rounded-xl mb-4 flex items-center justify-center bg-${tool.color}-500/20 text-${tool.color}-500 group-hover:scale-110 transition-transform`}>
                                    <tool.icon className="w-6 h-6" />
                                </div>
                                <h3 className="text-lg font-bold text-mono-900 mb-2 group-hover:text-mono-700 transition-colors">{tool.name}</h3>
                                <p className="text-sm text-mono-600 mb-4 h-10">{tool.desc}</p>
                                <div className="flex items-center text-xs font-medium text-mono-500 group-hover:text-mono-700 transition-colors">
                                    Launch Tool <ArrowRight className="w-3 h-3 ml-1 group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>

                <div className="onyx-card p-6">
                    <div className="flex items-start space-x-4">
                        <div className="p-3 bg-white/10 rounded-full text-white"><Briefcase className="w-6 h-6" /></div>
                        <div>
                            <h3 className="text-lg font-bold text-white mb-1">Need Personalized Advice?</h3>
                            <p className="text-sm text-mono-300 mb-3">Our AI Financial Coach can guide you through these tools step-by-step based on your specific situation.</p>
                            <a href="/dashboard/chat" className="text-xs font-bold text-green-400 hover:text-green-300">Start a chat &rarr;</a>
                        </div>
                    </div>
                </div>
            </div>
            <ToolModal tool={selectedTool} isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
        </DashboardLayout>
    )
}
