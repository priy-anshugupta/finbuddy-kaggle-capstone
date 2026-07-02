import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface DashboardSummary {
    total_balance: number
    monthly_income: number
    monthly_expenses: number
    savings_rate: number
    investment_value: number
    net_worth: number
}

interface SpendingTrend {
    category: string
    amount: number
    percentage: number
    trend: 'up' | 'down' | 'stable'
}

interface UpcomingPayment {
    id: string
    name: string
    amount: number
    due_date: string
    category: string
}

interface Alert {
    id: string
    type: 'info' | 'warning' | 'danger'
    title: string
    message: string
    created_at: string
}

interface DashboardState {
    summary: DashboardSummary | null
    spendingTrends: SpendingTrend[]
    upcomingPayments: UpcomingPayment[]
    alerts: Alert[]
    isLoading: boolean
    error: string | null
}

const initialState: DashboardState = {
    summary: null,
    spendingTrends: [],
    upcomingPayments: [],
    alerts: [],
    isLoading: false,
    error: null,
}

export const fetchDashboardSummary = createAsyncThunk(
    'dashboard/fetchSummary',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/dashboard/summary')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch summary')
        }
    }
)

export const fetchSpendingTrends = createAsyncThunk(
    'dashboard/fetchSpendingTrends',
    async (period: string = 'month', { rejectWithValue }) => {
        try {
            const response = await api.get(`/dashboard/spending-trends?period=${period}`)
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch trends')
        }
    }
)

export const fetchUpcomingPayments = createAsyncThunk(
    'dashboard/fetchUpcomingPayments',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/dashboard/upcoming-payments')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch payments')
        }
    }
)

export const fetchAlerts = createAsyncThunk(
    'dashboard/fetchAlerts',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/dashboard/alerts')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to fetch alerts')
        }
    }
)

const dashboardSlice = createSlice({
    name: 'dashboard',
    initialState,
    reducers: {
        clearAlerts: (state) => {
            state.alerts = []
        },
        dismissAlert: (state, action: PayloadAction<string>) => {
            state.alerts = state.alerts.filter((a) => a.id !== action.payload)
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDashboardSummary.pending, (state) => {
                state.isLoading = true
            })
            .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
                state.isLoading = false
                state.summary = action.payload
            })
            .addCase(fetchDashboardSummary.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            .addCase(fetchSpendingTrends.fulfilled, (state, action) => {
                state.spendingTrends = action.payload
            })
            .addCase(fetchUpcomingPayments.fulfilled, (state, action) => {
                state.upcomingPayments = action.payload
            })
            .addCase(fetchAlerts.fulfilled, (state, action) => {
                state.alerts = action.payload
            })
    },
})

export const { clearAlerts, dismissAlert } = dashboardSlice.actions
export default dashboardSlice.reducer
