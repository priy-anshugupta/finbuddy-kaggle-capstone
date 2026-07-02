import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface Transaction {
    id: string
    amount: number
    type: 'credit' | 'debit'
    category: string
    subcategory?: string
    merchant: string
    description?: string
    date: string
    is_recurring: boolean
}

interface TransactionStats {
    total_income: number
    total_expenses: number
    net: number
    by_category: Record<string, number>
}

interface TransactionsState {
    transactions: Transaction[]
    stats: TransactionStats | null
    filters: {
        startDate?: string
        endDate?: string
        category?: string
        type?: string
    }
    pagination: {
        page: number
        limit: number
        total: number
    }
    isLoading: boolean
    error: string | null
}

const initialState: TransactionsState = {
    transactions: [],
    stats: null,
    filters: {},
    pagination: {
        page: 1,
        limit: 20,
        total: 0,
    },
    isLoading: false,
    error: null,
}

export const fetchTransactions = createAsyncThunk(
    'transactions/fetch',
    async (params: { page?: number; limit?: number; category?: string }, { rejectWithValue }) => {
        try {
            const response = await api.get('/transactions', { params })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch transactions')
        }
    }
)

export const createTransaction = createAsyncThunk(
    'transactions/create',
    async (transaction: Partial<Transaction>, { rejectWithValue }) => {
        try {
            const response = await api.post('/transactions', transaction)
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to create transaction')
        }
    }
)

export const fetchTransactionStats = createAsyncThunk(
    'transactions/fetchStats',
    async (period: string = 'month', { rejectWithValue }) => {
        try {
            const response = await api.get(`/transactions/stats?period=${period}`)
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch stats')
        }
    }
)

const transactionsSlice = createSlice({
    name: 'transactions',
    initialState,
    reducers: {
        setFilters: (state, action: PayloadAction<typeof initialState.filters>) => {
            state.filters = action.payload
        },
        clearFilters: (state) => {
            state.filters = {}
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchTransactions.pending, (state) => {
                state.isLoading = true
            })
            .addCase(fetchTransactions.fulfilled, (state, action) => {
                state.isLoading = false
                state.transactions = action.payload.items || action.payload
                state.pagination.total = action.payload.total || action.payload.length
            })
            .addCase(fetchTransactions.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            .addCase(createTransaction.fulfilled, (state, action) => {
                state.transactions.unshift(action.payload)
            })
            .addCase(fetchTransactionStats.fulfilled, (state, action) => {
                state.stats = action.payload
            })
    },
})

export const { setFilters, clearFilters } = transactionsSlice.actions
export default transactionsSlice.reducer
