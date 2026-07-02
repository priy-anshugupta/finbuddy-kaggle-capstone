import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface Investment {
    id: string
    name: string
    type: 'stocks' | 'mutual_funds' | 'fd' | 'ppf' | 'nps' | 'bonds' | 'gold' | 'real_estate'
    amount_invested: number
    current_value: number
    returns: number
    returns_percentage: number
    platform?: string
}

interface PortfolioSummary {
    total_invested: number
    current_value: number
    total_returns: number
    returns_percentage: number
    allocation: Record<string, number>
}

interface WatchlistItem {
    id: string
    symbol: string
    name: string
    price: number
    change: number
    change_percentage: number
}

interface AgentRecommendation {
    type: 'growth' | 'safety'
    name: string
    description: string
    expected_return?: string
    risk_level?: string
}

interface AgentInsights {
    analysis: string
    growth_recommendations: AgentRecommendation[]
    safety_recommendations: AgentRecommendation[]
    market_news?: string
    aggregated_advice?: string
}

interface InvestmentsState {
    investments: Investment[]
    portfolio: PortfolioSummary | null
    watchlist: WatchlistItem[]
    agentInsights: AgentInsights | null
    isLoading: boolean
    isLoadingInsights: boolean
    error: string | null
}

const initialState: InvestmentsState = {
    investments: [],
    portfolio: null,
    watchlist: [],
    agentInsights: null,
    isLoading: false,
    isLoadingInsights: false,
    error: null,
}

export const fetchInvestments = createAsyncThunk(
    'investments/fetch',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/investments')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch investments')
        }
    }
)

export const fetchPortfolioSummary = createAsyncThunk(
    'investments/fetchPortfolio',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/investments/portfolio/summary')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch portfolio')
        }
    }
)

export const fetchWatchlist = createAsyncThunk(
    'investments/fetchWatchlist',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/investments/watchlist')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch watchlist')
        }
    }
)

export const addToWatchlist = createAsyncThunk(
    'investments/addToWatchlist',
    async (symbol: string, { rejectWithValue }) => {
        try {
            const response = await api.post('/investments/watchlist', { symbol })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to add to watchlist')
        }
    }
)

export const fetchAgentInsights = createAsyncThunk(
    'investments/fetchAgentInsights',
    async (query: string | undefined, { rejectWithValue }) => {
        try {
            const response = await api.post('/insights/investment-advisory', {
                query: query || null,
                include_news: true
            }, {
                timeout: 90000,
            })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch AI insights')
        }
    }
)

const investmentsSlice = createSlice({
    name: 'investments',
    initialState,
    reducers: {
        removeFromWatchlist: (state, action: PayloadAction<string>) => {
            state.watchlist = state.watchlist.filter((item) => item.id !== action.payload)
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchInvestments.pending, (state) => {
                state.isLoading = true
            })
            .addCase(fetchInvestments.fulfilled, (state, action) => {
                state.isLoading = false
                state.investments = action.payload
            })
            .addCase(fetchInvestments.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            .addCase(fetchPortfolioSummary.fulfilled, (state, action) => {
                state.portfolio = action.payload
            })
            .addCase(fetchWatchlist.fulfilled, (state, action) => {
                state.watchlist = action.payload
            })
            .addCase(addToWatchlist.fulfilled, (state, action) => {
                state.watchlist.push(action.payload)
            })
            .addCase(fetchAgentInsights.pending, (state) => {
                state.isLoadingInsights = true
                state.error = null
            })
            .addCase(fetchAgentInsights.fulfilled, (state, action) => {
                state.isLoadingInsights = false
                state.agentInsights = action.payload
                state.error = null
            })
            .addCase(fetchAgentInsights.rejected, (state, action) => {
                state.isLoadingInsights = false
                state.error = action.payload as string
            })
    },
})

export const { removeFromWatchlist } = investmentsSlice.actions
export default investmentsSlice.reducer
