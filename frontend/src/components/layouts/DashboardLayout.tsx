'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
    LayoutDashboard,
    Wallet,
    TrendingUp,
    MessageCircle,
    CreditCard,
    Settings,
    LogOut,
    Menu,
    X,
    Bell,
    Search,
    Sparkles,
    ChevronDown,
    User,
    Globe,
    Briefcase,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { logout } from '@/store/slices/authSlice'

const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Transactions', href: '/dashboard/transactions', icon: Wallet },
    { name: 'Investments', href: '/dashboard/investments', icon: TrendingUp },
    { name: 'Market News', href: '/dashboard/news', icon: Globe },
    { name: 'Financial Tools', href: '/dashboard/tools', icon: Briefcase },
    { name: 'AI Coach', href: '/dashboard/chat', icon: MessageCircle },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

interface DashboardLayoutProps {
    children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
    const [sidebarOpen, setSidebarOpen] = useState(false)
    const [userMenuOpen, setUserMenuOpen] = useState(false)
    const pathname = usePathname()
    const dispatch = useAppDispatch()
    const { user } = useAppSelector((state) => state.auth)

    const handleLogout = () => {
        dispatch(logout())
        window.location.href = '/'
    }

    return (
        <div className="min-h-screen flex">
            {/* Mobile sidebar backdrop */}
            <AnimatePresence>
                {sidebarOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={() => setSidebarOpen(false)}
                        className="fixed inset-0 z-40 bg-mono-900/20 backdrop-blur-sm lg:hidden"
                    />
                )}
            </AnimatePresence>

            {/* Sidebar - Floating Glass */}
            <aside
                className={cn(
                    'fixed inset-y-4 left-4 z-50 w-72 sidebar-glass transform transition-transform duration-300 lg:translate-x-0',
                    sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
                )}
            >
                <div className="flex flex-col h-full">
                    {/* Logo */}
                    <div className="flex items-center justify-between h-16 px-6 border-b border-mono-200/50">
                        <Link href="/dashboard" className="flex items-center space-x-2">
                            <div className="w-10 h-10 rounded-xl bg-mono-900 flex items-center justify-center">
                                <Sparkles className="w-6 h-6 text-white" />
                            </div>
                            <span className="text-xl font-display font-bold text-mono-900 tracking-tight">FinBuddy</span>
                        </Link>
                        <button
                            onClick={() => setSidebarOpen(false)}
                            className="lg:hidden text-mono-500 hover:text-mono-900 transition-all duration-300"
                        >
                            <X className="w-6 h-6" />
                        </button>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto custom-scrollbar">
                        {navigation.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={cn(
                                        'nav-link',
                                        isActive && 'nav-link-active'
                                    )}
                                >
                                    <item.icon className={cn('w-5 h-5', isActive ? 'text-white' : 'text-mono-500')} />
                                    <span>{item.name}</span>
                                </Link>
                            )
                        })}
                    </nav>

                    {/* AI Assistant Quick Access - Onyx Card */}
                    <div className="p-4 mx-4 mb-4 onyx-card">
                        <div className="flex items-center space-x-3 mb-3">
                            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center">
                                <MessageCircle className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-white">AI Assistant</p>
                                <p className="text-xs text-white/50">Online & Ready</p>
                            </div>
                        </div>
                        <Link
                            href="/dashboard/chat"
                            className="block w-full text-center text-sm py-2.5 bg-white text-mono-900 font-medium rounded-xl hover:bg-mono-100 transition-all duration-300"
                        >
                            Start Chat
                        </Link>
                    </div>

                    {/* User / Logout */}
                    <div className="p-4 border-t border-mono-200/50">
                        <button
                            onClick={handleLogout}
                            className="flex items-center space-x-3 w-full px-4 py-3 text-mono-500 hover:text-mono-900 hover:bg-mono-100 rounded-xl transition-all duration-300"
                        >
                            <LogOut className="w-5 h-5" />
                            <span className="font-medium">Logout</span>
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-h-screen lg:ml-80">
                {/* Top Bar - Glass */}
                <header className="sticky top-4 z-30 mx-4 lg:mx-8 mt-4 glass-card">
                    <div className="flex items-center justify-between h-16 px-6">
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={() => setSidebarOpen(true)}
                                className="lg:hidden text-mono-500 hover:text-mono-900 transition-all duration-300"
                            >
                                <Menu className="w-6 h-6" />
                            </button>

                            {/* Search */}
                            <div className="hidden md:flex items-center">
                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-mono-400" />
                                    <input
                                        type="text"
                                        placeholder="Search transactions, investments..."
                                        className="w-80 pl-10 pr-4 py-2.5 bg-mono-100/50 border border-mono-200 rounded-xl text-sm text-mono-900 placeholder:text-mono-400 focus:outline-none focus:border-mono-400 focus:bg-white transition-all duration-300"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            {/* Notifications */}
                            <button className="relative p-2.5 text-mono-500 hover:text-mono-900 hover:bg-mono-100 rounded-xl transition-all duration-300">
                                <Bell className="w-5 h-5" />
                                <span className="absolute top-2 right-2 w-2 h-2 bg-mono-900 rounded-full" />
                            </button>

                            {/* User Menu */}
                            <div className="relative">
                                <button
                                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                                    className="flex items-center space-x-3 px-3 py-2 rounded-xl hover:bg-mono-100 transition-all duration-300"
                                >
                                    <div className="w-8 h-8 rounded-xl bg-mono-900 flex items-center justify-center">
                                        <User className="w-4 h-4 text-white" />
                                    </div>
                                    <span className="hidden md:block text-sm text-mono-900 font-medium">
                                        {user?.full_name || 'User'}
                                    </span>
                                    <ChevronDown className="w-4 h-4 text-mono-400" />
                                </button>

                                <AnimatePresence>
                                    {userMenuOpen && (
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: 10 }}
                                            className="absolute right-0 mt-2 w-48 glass-card p-2 shadow-lg"
                                        >
                                            <Link
                                                href="/dashboard/settings"
                                                className="block px-4 py-2.5 text-sm text-mono-700 hover:bg-mono-100 rounded-xl transition-all duration-300 font-medium"
                                            >
                                                Settings
                                            </Link>
                                            <button
                                                onClick={handleLogout}
                                                className="w-full text-left px-4 py-2.5 text-sm text-mono-700 hover:bg-mono-100 rounded-xl transition-all duration-300 font-medium"
                                            >
                                                Logout
                                            </button>
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 p-4 lg:p-8">
                    {children}
                </main>
            </div>
        </div>
    )
}
