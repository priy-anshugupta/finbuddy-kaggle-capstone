'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Mail, Lock, Sparkles } from 'lucide-react'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { login } from '@/store/slices/authSlice'
import toast from 'react-hot-toast'

interface LoginForm {
    email: string
    password: string
}

export default function LoginPage() {
    const [showPassword, setShowPassword] = useState(false)
    const dispatch = useAppDispatch()
    const { isLoading, error } = useAppSelector((state: any) => state.auth)
    const router = useRouter()

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginForm>()

    const onSubmit = async (data: LoginForm) => {
        try {
            await dispatch(login(data)).unwrap()
            toast.success('Welcome back!')
            router.push('/dashboard')
        } catch (err) {
            toast.error(err as string)
        }
    }

    return (
        <main className="min-h-screen flex items-center justify-center px-4">
            {/* Background Effects - Subtle */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-1/2 -right-1/4 w-[600px] h-[600px] bg-mono-200/30 rounded-full blur-3xl" />
                <div className="absolute -bottom-1/4 -left-1/4 w-[500px] h-[500px] bg-mono-100/50 rounded-full blur-3xl" />
            </div>

            <motion.div
                className="w-full max-w-md"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                {/* Logo */}
                <div className="text-center mb-8">
                    <Link href="/" className="inline-flex items-center space-x-2">
                        <div className="w-12 h-12 rounded-xl bg-mono-900 flex items-center justify-center">
                            <Sparkles className="w-7 h-7 text-white" />
                        </div>
                        <span className="text-2xl font-display font-bold text-mono-900 tracking-tight">FinBuddy</span>
                    </Link>
                </div>

                {/* Login Card - Glass Formula */}
                <div className="glass-card p-8">
                    <h1 className="text-2xl font-bold text-mono-900 mb-2 tracking-tight">Welcome back</h1>
                    <p className="text-mono-500 mb-8 font-medium">Sign in to continue to your dashboard</p>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-mono-700 mb-2">
                                Email
                            </label>
                            <div className="relative">
                                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-mono-400" />
                                <input
                                    type="email"
                                    {...register('email', { required: 'Email is required' })}
                                    className="input-field pl-12"
                                    placeholder="you@example.com"
                                />
                            </div>
                            {errors.email && (
                                <p className="text-mono-700 text-sm mt-1 font-medium">{errors.email.message}</p>
                            )}
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-sm font-medium text-mono-700 mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-mono-400" />
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    {...register('password', { required: 'Password is required' })}
                                    className="input-field pl-12 pr-12"
                                    placeholder="••••••••"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-mono-400 hover:text-mono-700 transition-all duration-300"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            {errors.password && (
                                <p className="text-mono-700 text-sm mt-1 font-medium">{errors.password.message}</p>
                            )}
                        </div>

                        {/* Forgot Password */}
                        <div className="flex justify-end">
                            <Link href="/forgot-password" className="text-sm text-mono-700 hover:text-mono-900 font-medium transition-all duration-300">
                                Forgot password?
                            </Link>
                        </div>

                        {/* Submit */}
                        <button
                            type="submit"
                            disabled={isLoading}
                            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center space-x-2">
                                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                            fill="none"
                                        />
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                                        />
                                    </svg>
                                    <span>Signing in...</span>
                                </span>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    {/* Register Link */}
                    <p className="text-center text-mono-500 mt-6 font-medium">
                        Don't have an account?{' '}
                        <Link href="/register" className="text-mono-900 hover:underline font-semibold">
                            Sign up
                        </Link>
                    </p>
                </div>
            </motion.div>
        </main>
    )
}
