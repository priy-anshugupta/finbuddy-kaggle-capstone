'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface MarkdownRendererProps {
    content: string
    className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
    return (
        <div className={`prose prose-sm max-w-none ${className}`}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                    // Style headings
                    h1: ({ children }) => (
                        <h1 className="text-xl font-bold text-mono-900 mt-4 mb-2">{children}</h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-lg font-semibold text-mono-900 mt-3 mb-2">{children}</h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-base font-semibold text-mono-800 mt-2 mb-1">{children}</h3>
                    ),
                    // Style paragraphs
                    p: ({ children }) => (
                        <p className="text-mono-700 mb-2 leading-relaxed">{children}</p>
                    ),
                    // Style lists
                    ul: ({ children }) => (
                        <ul className="list-disc list-inside space-y-1 mb-2 text-mono-700">{children}</ul>
                    ),
                    ol: ({ children }) => (
                        <ol className="list-decimal list-inside space-y-1 mb-2 text-mono-700">{children}</ol>
                    ),
                    li: ({ children }) => (
                        <li className="text-mono-700">{children}</li>
                    ),
                    // Style links
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-mono-900 hover:text-mono-700 underline"
                        >
                            {children}
                        </a>
                    ),
                    // Style strong/bold
                    strong: ({ children }) => (
                        <strong className="font-semibold text-mono-900">{children}</strong>
                    ),
                    // Style emphasis/italic
                    em: ({ children }) => (
                        <em className="italic text-mono-700">{children}</em>
                    ),
                    // Style code blocks
                    code: ({ children, className }) => {
                        const isInline = !className
                        return isInline ? (
                            <code className="bg-mono-200 px-1.5 py-0.5 rounded text-sm text-mono-800">
                                {children}
                            </code>
                        ) : (
                            <code className="block bg-mono-100 p-3 rounded-lg text-sm overflow-x-auto text-mono-800">
                                {children}
                            </code>
                        )
                    },
                    // Style blockquotes
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-mono-400 pl-4 py-1 my-2 bg-mono-100 rounded-r">
                            {children}
                        </blockquote>
                    ),
                    // Style horizontal rules
                    hr: () => <hr className="border-mono-300 my-4" />,
                    // Style tables
                    table: ({ children }) => (
                        <div className="overflow-x-auto my-2">
                            <table className="min-w-full border-collapse">{children}</table>
                        </div>
                    ),
                    th: ({ children }) => (
                        <th className="border border-mono-300 px-3 py-2 bg-mono-200 text-left text-mono-900 font-semibold">
                            {children}
                        </th>
                    ),
                    td: ({ children }) => (
                        <td className="border border-mono-200 px-3 py-2 text-mono-700">{children}</td>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    )
}
