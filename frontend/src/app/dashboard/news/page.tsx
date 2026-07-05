'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
    Newspaper,
    TrendingUp,
    TrendingDown,
    Globe,
    Share2,
    Bookmark,
    ExternalLink,
    MessageCircle,
    Loader2,
    RefreshCw,
    ImageOff,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { formatDate } from '@/lib/utils'
import { api } from '@/lib/api'

interface NewsItem {
    id: number
    title: string
    summary: string
    source: string
    sentiment: string
    impact: string
    date: string
    category: string
    imageUrl: string
    url: string
}

// Image component with fallback
function NewsImage({ src, alt, className }: { src: string; alt: string; className?: string }) {
    const [imgError, setImgError] = useState(false)
    const [isLoading, setIsLoading] = useState(true)

    const fallbackImages = [
        'https://images.unsplash.com/photo-1611974765270-ca1258634369?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&auto=format&fit=crop',
        'https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800&auto=format&fit=crop',
    ]

    const handleError = () => {
        setImgError(true)
        setIsLoading(false)
    }

    const imageSrc = imgError 
        ? fallbackImages[Math.floor(Math.random() * fallbackImages.length)]
        : src

    return (
        <div className={`relative ${className}`}>
            {isLoading && (
                <div className="absolute inset-0 bg-slate-800 flex items-center justify-center">
                    <Loader2 className="w-6 h-6 animate-spin text-slate-500" />
                </div>
            )}
            <img
                src={imageSrc}
                alt={alt}
                className={`w-full h-full object-cover transition-all duration-500 ${isLoading ? 'opacity-0' : 'opacity-100'}`}
                onError={handleError}
                onLoad={() => setIsLoading(false)}
            />
            {imgError && !isLoading && (
                <div className="absolute bottom-2 right-2 bg-slate-900/80 rounded px-2 py-1">
                    <ImageOff className="w-3 h-3 text-slate-400" />
                </div>
            )}
        </div>
    )
}

export default function NewsPage() {
    const [filter, setFilter] = useState<'all' | 'market' | 'economy' | 'tech'>('all')
    const [newsItems, setNewsItems] = useState<NewsItem[]>([])
    const [isLoading, setIsLoading] = useState(false)

    const fetchNews = async () => {
        setIsLoading(true)
        try {
            const response = await api.get('/insights/market-news')
            if (response.data?.news && Array.isArray(response.data.news)) {
                const apiNews = response.data.news.map((item: any, idx: number) => ({
                    id: idx + 1,
                    title: item.title || 'Market Update',
                    summary: item.summary || item.description || '',
                    source: item.source || 'FinBuddy AI',
                    sentiment: item.sentiment || 'Neutral',
                    impact: item.impact || 'Review your portfolio.',
                    date: item.date || new Date().toISOString(),
                    category: item.category?.toLowerCase() || 'market',
                    imageUrl: item.imageUrl || `https://images.unsplash.com/photo-1611974765270-ca1258634369?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3`,
                    url: item.url || '',
                }))
                setNewsItems(apiNews)
            } else {
                // If no news from API, show empty state
                setNewsItems([])
            }
        } catch (error) {
            console.error('Failed to fetch news:', error)
            setNewsItems([])
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        fetchNews()
    }, [])

    const filteredNews = filter === 'all' ? newsItems : newsItems.filter((n: NewsItem) => n.category === filter)

    return (
        <DashboardLayout>
            <div className="space-y-8">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-mono-900">Market Intelligence</h1>
                        <p className="text-mono-500">Curated financial news and sentiment analysis</p>
                    </div>

                    <div className="flex space-x-2 overflow-x-auto pb-2 md:pb-0">
                        {['all', 'market', 'economy', 'tech'].map((cat) => (
                            <button
                                key={cat}
                                onClick={() => setFilter(cat as any)}
                                className={`px-4 py-2 rounded-full text-sm font-medium capitalize transition-all ${filter === cat
                                    ? 'bg-mono-900 text-white shadow-lg'
                                    : 'bg-mono-200 text-mono-600 hover:text-mono-900 hover:bg-mono-300'
                                    }`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Featured Story */}
                {newsItems.length > 1 && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="relative h-96 rounded-2xl overflow-hidden group cursor-pointer"
                        onClick={() => newsItems[1].url && window.open(newsItems[1].url, '_blank', 'noopener,noreferrer')}
                    >
                        <div className="absolute inset-0">
                            <NewsImage
                                src={newsItems[1].imageUrl}
                                alt="Featured"
                                className="w-full h-full"
                            />
                            <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/50 to-transparent" />
                        </div>

                        <div className="absolute bottom-0 left-0 right-0 p-8">
                            <span className="inline-block px-3 py-1 bg-primary-500 text-white text-xs font-bold rounded-full mb-3">
                                FEATURED
                            </span>
                            <h2 className="text-3xl md:text-4xl font-bold text-white mb-3 group-hover:text-primary-400 transition-colors">
                                {newsItems[1].title}
                            </h2>
                            <p className="text-slate-300 max-w-2xl text-lg mb-4 line-clamp-2">
                                {newsItems[1].summary}
                            </p>
                            <div className="flex items-center space-x-4 text-sm text-slate-400">
                                <span className="flex items-center">
                                    <Globe className="w-4 h-4 mr-1" />
                                    {newsItems[1].source}
                                </span>
                                <span>•</span>
                                <span>{formatDate(newsItems[1].date)}</span>
                                {newsItems[1].url && (
                                    <>
                                        <span>•</span>
                                        <span className="flex items-center text-primary-400">
                                            <ExternalLink className="w-4 h-4 mr-1" />
                                            Read Article
                                        </span>
                                    </>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}

                {/* News Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredNews.map((news: NewsItem, idx: number) => (
                        <motion.div
                            key={news.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="glass-card overflow-hidden hover:border-primary-500/50 transition-all group flex flex-col h-full"
                        >
                            <div className="relative h-48 overflow-hidden">
                                <NewsImage
                                    src={news.imageUrl}
                                    alt={news.title}
                                    className="h-full transition-transform duration-500 group-hover:scale-110"
                                />
                                <div className="absolute top-4 right-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${news.sentiment === 'Positive' ? 'bg-green-500/90 text-white' :
                                        news.sentiment === 'Negative' ? 'bg-red-500/90 text-white' :
                                            'bg-slate-500/90 text-white'
                                        }`}>
                                        {news.sentiment}
                                    </span>
                                </div>
                            </div>

                            <div className="p-5 flex-1 flex flex-col">
                                <div className="flex items-center space-x-2 mb-3 text-xs text-mono-500">
                                    <span className="text-mono-700 font-medium uppercase">{news.source}</span>
                                    <span>•</span>
                                    <span>{formatDate(news.date)}</span>
                                </div>

                                <h3 className="text-lg font-bold text-mono-900 mb-2 line-clamp-2 group-hover:text-mono-700 transition-colors">
                                    {news.title}
                                </h3>

                                <p className="text-sm text-mono-600 mb-4 line-clamp-3 flex-1">
                                    {news.summary}
                                </p>

                                <div className="p-3 bg-mono-100 rounded-lg border border-mono-200 mb-4">
                                    <p className="text-xs text-mono-700">
                                        <span className="text-mono-900 font-bold">AI Insight:</span> {news.impact}
                                    </p>
                                </div>

                                <div className="flex items-center justify-between pt-4 border-t border-mono-200">
                                    <button 
                                        className="text-mono-400 hover:text-mono-700 transition-colors"
                                        onClick={(e) => {
                                            e.stopPropagation()
                                            if (navigator.share) {
                                                navigator.share({
                                                    title: news.title,
                                                    text: news.summary,
                                                    url: news.url || window.location.href
                                                })
                                            } else if (news.url) {
                                                navigator.clipboard.writeText(news.url)
                                            }
                                        }}
                                    >
                                        <Share2 className="w-5 h-5" />
                                    </button>
                                    <a
                                        href={news.url || '#'}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={(e) => {
                                            if (!news.url) e.preventDefault()
                                        }}
                                        className={`flex items-center text-sm font-medium transition-colors ${
                                            news.url 
                                                ? 'text-mono-700 hover:text-mono-900 cursor-pointer' 
                                                : 'text-mono-400 cursor-not-allowed'
                                        }`}
                                    >
                                        Read Full Story <ExternalLink className="w-4 h-4 ml-1" />
                                    </a>
                                    <button className="text-mono-400 hover:text-mono-700 transition-colors">
                                        <Bookmark className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
                
                {/* Loading State */}
                {isLoading && (
                    <div className="flex items-center justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-mono-500" />
                        <span className="ml-3 text-mono-500">Fetching latest news...</span>
                    </div>
                )}
                
                {/* Empty State */}
                {!isLoading && filteredNews.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                        <Newspaper className="w-16 h-16 text-mono-400 mb-4" />
                        <h3 className="text-lg font-semibold text-mono-900 mb-2">No News Available</h3>
                        <p className="text-mono-500 mb-4">We couldn't find any news articles at the moment.</p>
                        <button
                            onClick={fetchNews}
                            className="flex items-center px-4 py-2 bg-mono-900 text-white rounded-lg hover:bg-mono-800 transition-colors"
                        >
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Refresh News
                        </button>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
