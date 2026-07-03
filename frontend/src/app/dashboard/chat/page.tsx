'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Send,
    Mic,
    Paperclip,
    Bot,
    User,
    Sparkles,
    Plus,
    MessageCircle,
    Trash2,
    MoreVertical,
} from 'lucide-react'
import { DashboardLayout } from '@/components/layouts/DashboardLayout'
import { formatRelativeTime } from '@/lib/utils'
import { useAppDispatch, useAppSelector, RootState } from '@/store/hooks'
import { api } from '@/lib/api'
import {
    fetchConversations,
    createConversation,
    fetchMessages,
    addMessage,
    setCurrentConversation,
} from '@/store/slices/chatSlice'

const quickPrompts = [
    '📊 Analyze my spending this month',
    '💡 How can I save more money?',
    '📈 Should I invest in stocks?',
    '💳 Recommend a credit card for me',
    '📋 Calculate my income tax',
    '🏦 Help me plan for retirement',
]

export default function ChatPage() {
    const [input, setInput] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)

    const dispatch = useAppDispatch()
    const { conversations, currentConversation, messages, isLoading, isStreaming } = useAppSelector(
        (state: any) => state.chat
    )

    // Demo messages
    const demoMessages = [
        {
            id: '1',
            role: 'assistant' as const,
            content: "Hello! I'm your AI Financial Coach. I can help you with:\n\n• **Spending Analysis** - Understand where your money goes\n• **Investment Advice** - Get personalized recommendations\n• **Tax Planning** - Optimize your taxes\n• **Credit Cards** - Find the best cards for you\n\nHow can I assist you today?",
            timestamp: new Date().toISOString(),
            agent_name: 'FinBuddy',
        },
    ]

    const displayMessages = messages.length ? messages : demoMessages

    useEffect(() => {
        dispatch(fetchConversations())
    }, [dispatch])

    useEffect(() => {
        scrollToBottom()
    }, [displayMessages])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    const handleSend = async () => {
        if (!input.trim() || isLoading) return

        const userMessage = {
            id: Date.now().toString(),
            role: 'user' as const,
            content: input,
            timestamp: new Date().toISOString(),
        }

        dispatch(addMessage(userMessage))
        setInput('')
        setIsTyping(true)

        try {
            // Call the actual chat API
            const response = await api.post('/chat/send', {
                message: userMessage.content,
                conversation_id: currentConversation?.id,
                context: {}
            })

            const aiResponse = {
                id: (Date.now() + 1).toString(),
                role: 'assistant' as const,
                content: response.data.message,
                timestamp: new Date().toISOString(),
                agent_name: response.data.agent_name || 'FinBuddy',
            }
            dispatch(addMessage(aiResponse))

            // If suggestions are returned, you could use them
            if (response.data.suggestions) {
                console.log('AI Suggestions:', response.data.suggestions)
            }
        } catch (error: any) {
            console.error('Chat API error:', error)
            // Fallback error message
            const errorResponse = {
                id: (Date.now() + 1).toString(),
                role: 'assistant' as const,
                content: "I'm sorry, I couldn't process your request right now. Please check if the backend server is running and try again.",
                timestamp: new Date().toISOString(),
                agent_name: 'FinBuddy',
            }
            dispatch(addMessage(errorResponse))
        } finally {
            setIsTyping(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleQuickPrompt = (prompt: string) => {
        setInput(prompt.replace(/^[^\s]+\s/, ''))
        inputRef.current?.focus()
    }

    const handleNewChat = () => {
        dispatch(createConversation('New Chat'))
    }

    return (
        <DashboardLayout>
            <div className="flex h-[calc(100vh-8rem)] gap-6">
                {/* Sidebar - Conversations - Glass Card */}
                <div className="hidden lg:flex w-72 glass-card p-4 flex-col">
                    <button
                        onClick={handleNewChat}
                        className="btn-primary w-full mb-4 flex items-center justify-center space-x-2"
                    >
                        <Plus className="w-5 h-5" />
                        <span>New Chat</span>
                    </button>

                    <div className="flex-1 overflow-y-auto custom-scrollbar space-y-2">
                        {(conversations.length ? conversations : [
                            { id: '1', title: 'Spending Analysis', created_at: new Date().toISOString(), updated_at: new Date().toISOString(), message_count: 5 },
                            { id: '2', title: 'Investment Planning', created_at: new Date().toISOString(), updated_at: new Date().toISOString(), message_count: 3 },
                        ]).map((conv: any) => (
                            <button
                                key={conv.id}
                                className={`w-full text-left p-3 rounded-xl transition-all duration-300 ${currentConversation?.id === conv.id
                                    ? 'bg-mono-900 text-white'
                                    : 'hover:bg-mono-100 text-mono-700'
                                    }`}
                                onClick={() => dispatch(setCurrentConversation(conv))}
                            >
                                <div className="flex items-center space-x-3">
                                    <MessageCircle className={`w-4 h-4 ${currentConversation?.id === conv.id ? 'text-white' : 'text-mono-500'}`} />
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium truncate">{conv.title}</p>
                                        <p className={`text-xs ${currentConversation?.id === conv.id ? 'text-white/60' : 'text-mono-500'}`}>{formatRelativeTime(conv.created_at)}</p>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Chat Area - Glass Card */}
                <div className="flex-1 glass-card flex flex-col">
                    {/* Chat Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b border-mono-200/50">
                        <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-xl bg-mono-900 flex items-center justify-center">
                                <Sparkles className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h2 className="font-semibold text-mono-900 tracking-tight">AI Financial Coach</h2>
                                <p className="text-xs text-mono-500 flex items-center font-medium">
                                    <span className="w-2 h-2 bg-mono-900 rounded-full mr-1"></span>
                                    Online • Gemini 2.5 Flash
                                </p>
                            </div>
                        </div>
                        <button className="p-2.5 text-mono-500 hover:text-mono-900 rounded-xl hover:bg-mono-100 transition-all duration-300">
                            <MoreVertical className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-6">
                        {displayMessages.map((message: any) => (
                            <motion.div
                                key={message.id}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div className={`flex items-start space-x-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${message.role === 'user'
                                        ? 'bg-mono-900'
                                        : 'bg-mono-200'
                                        }`}>
                                        {message.role === 'user' ? (
                                            <User className="w-4 h-4 text-white" />
                                        ) : (
                                            <Bot className="w-4 h-4 text-mono-700" />
                                        )}
                                    </div>
                                    <div className={message.role === 'user' ? 'chat-message-user' : 'chat-message-assistant'}>
                                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                                            {message.content.split('\n').map((line: string, i: number) => (
                                                <p key={i} className={line.startsWith('•') || line.startsWith('-') ? 'ml-2' : ''}>
                                                    {line.split('**').map((part: string, j: number) =>
                                                        j % 2 === 1 ? <strong key={j}>{part}</strong> : part
                                                    )}
                                                </p>
                                            ))}
                                        </div>
                                        <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-white/60' : 'text-mono-400'}`}>
                                            {formatRelativeTime(message.timestamp)}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}

                        {/* Typing indicator */}
                        <AnimatePresence>
                            {isTyping && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    exit={{ opacity: 0, y: -10 }}
                                    className="flex items-center space-x-3"
                                >
                                    <div className="w-8 h-8 rounded-xl bg-mono-200 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-mono-700" />
                                    </div>
                                    <div className="chat-message-assistant">
                                        <div className="flex space-x-1">
                                            <span className="w-2 h-2 bg-mono-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                            <span className="w-2 h-2 bg-mono-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                            <span className="w-2 h-2 bg-mono-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                        </div>
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>

                        <div ref={messagesEndRef} />
                    </div>

                    {/* Quick Prompts */}
                    {displayMessages.length <= 1 && (
                        <div className="px-6 pb-4">
                            <p className="text-sm text-mono-500 mb-3 font-medium">Quick prompts:</p>
                            <div className="flex flex-wrap gap-2">
                                {quickPrompts.map((prompt, index) => (
                                    <button
                                        key={index}
                                        onClick={() => handleQuickPrompt(prompt)}
                                        className="px-3 py-2 bg-mono-100 hover:bg-mono-200 border border-mono-200 rounded-xl text-sm text-mono-700 transition-all duration-300 font-medium"
                                    >
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="p-4 border-t border-mono-200/50">
                        <div className="flex items-end space-x-3">
                            <button className="p-3 text-mono-500 hover:text-mono-900 hover:bg-mono-100 rounded-xl transition-all duration-300">
                                <Paperclip className="w-5 h-5" />
                            </button>

                            <div className="flex-1 relative">
                                <textarea
                                    ref={inputRef}
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Ask me anything about your finances..."
                                    rows={1}
                                    className="w-full px-4 py-3 bg-mono-100/50 border border-mono-200 rounded-xl text-mono-900 placeholder:text-mono-400 focus:outline-none focus:border-mono-400 focus:bg-white resize-none transition-all duration-300"
                                    style={{ minHeight: '48px', maxHeight: '120px' }}
                                />
                            </div>

                            <button className="p-3 text-mono-500 hover:text-mono-900 hover:bg-mono-100 rounded-xl transition-all duration-300">
                                <Mic className="w-5 h-5" />
                            </button>

                            <button
                                onClick={handleSend}
                                disabled={!input.trim() || isLoading}
                                className="btn-primary p-3 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <Send className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}
