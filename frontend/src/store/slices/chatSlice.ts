import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    agent_name?: string
    is_streaming?: boolean
}

interface Conversation {
    id: string
    title: string
    created_at: string
    updated_at: string
    message_count: number
}

interface ChatState {
    conversations: Conversation[]
    currentConversation: Conversation | null
    messages: Message[]
    isLoading: boolean
    isStreaming: boolean
    error: string | null
}

const initialState: ChatState = {
    conversations: [],
    currentConversation: null,
    messages: [],
    isLoading: false,
    isStreaming: false,
    error: null,
}

export const fetchConversations = createAsyncThunk(
    'chat/fetchConversations',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/chat/conversations')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch conversations')
        }
    }
)

export const createConversation = createAsyncThunk(
    'chat/createConversation',
    async (title: string | undefined, { rejectWithValue }) => {
        try {
            const response = await api.post('/chat/conversations', { title })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to create conversation')
        }
    }
)

export const fetchMessages = createAsyncThunk(
    'chat/fetchMessages',
    async (conversationId: string, { rejectWithValue }) => {
        try {
            const response = await api.get(`/chat/conversations/${conversationId}/messages`)
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch messages')
        }
    }
)

export const sendMessage = createAsyncThunk(
    'chat/sendMessage',
    async (
        { conversationId, content }: { conversationId: string; content: string },
        { rejectWithValue }
    ) => {
        try {
            const response = await api.post(`/chat/conversations/${conversationId}/messages`, { content })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to send message')
        }
    }
)

const chatSlice = createSlice({
    name: 'chat',
    initialState,
    reducers: {
        setCurrentConversation: (state, action: PayloadAction<Conversation | null>) => {
            state.currentConversation = action.payload
        },
        addMessage: (state, action: PayloadAction<Message>) => {
            state.messages.push(action.payload)
        },
        updateLastMessage: (state, action: PayloadAction<string>) => {
            if (state.messages.length > 0) {
                const lastMessage = state.messages[state.messages.length - 1]
                lastMessage.content += action.payload
            }
        },
        setStreaming: (state, action: PayloadAction<boolean>) => {
            state.isStreaming = action.payload
        },
        clearMessages: (state) => {
            state.messages = []
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchConversations.fulfilled, (state, action) => {
                state.conversations = action.payload
            })
            .addCase(createConversation.fulfilled, (state, action) => {
                state.conversations.unshift(action.payload)
                state.currentConversation = action.payload
                state.messages = []
            })
            .addCase(fetchMessages.pending, (state) => {
                state.isLoading = true
            })
            .addCase(fetchMessages.fulfilled, (state, action) => {
                state.isLoading = false
                state.messages = action.payload
            })
            .addCase(fetchMessages.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            .addCase(sendMessage.pending, (state) => {
                state.isLoading = true
            })
            .addCase(sendMessage.fulfilled, (state, action) => {
                state.isLoading = false
                // Message already added via addMessage action
            })
            .addCase(sendMessage.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
    },
})

export const {
    setCurrentConversation,
    addMessage,
    updateLastMessage,
    setStreaming,
    clearMessages,
} = chatSlice.actions

export default chatSlice.reducer
