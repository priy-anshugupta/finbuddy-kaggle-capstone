import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { api } from '@/lib/api'

interface User {
    id: string
    email: string
    full_name: string
    avatar_url?: string
    monthly_income?: number
    created_at: string
}

interface AuthState {
    user: User | null
    token: string | null
    refreshToken: string | null
    isAuthenticated: boolean
    isLoading: boolean
    error: string | null
}

const initialState: AuthState = {
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
}

export const login = createAsyncThunk(
    'auth/login',
    async ({ email, password }: { email: string; password: string }, { rejectWithValue }) => {
        try {
            const response = await api.post('/auth/login', { email, password })
            localStorage.setItem('token', response.data.access_token)
            localStorage.setItem('refreshToken', response.data.refresh_token)
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Login failed')
        }
    }
)

export const register = createAsyncThunk(
    'auth/register',
    async (
        { email, password, full_name }: { email: string; password: string; full_name: string },
        { rejectWithValue }
    ) => {
        try {
            const response = await api.post('/auth/register', { email, password, full_name })
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Registration failed')
        }
    }
)

export const getCurrentUser = createAsyncThunk(
    'auth/getCurrentUser',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/auth/me')
            return response.data
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.detail || 'Failed to get user')
        }
    }
)

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            state.user = null
            state.token = null
            state.refreshToken = null
            state.isAuthenticated = false
            localStorage.removeItem('token')
            localStorage.removeItem('refreshToken')
        },
        setToken: (state, action: PayloadAction<string>) => {
            state.token = action.payload
            state.isAuthenticated = true
        },
        clearError: (state) => {
            state.error = null
        },
    },
    extraReducers: (builder) => {
        builder
            // Login
            .addCase(login.pending, (state) => {
                state.isLoading = true
                state.error = null
            })
            .addCase(login.fulfilled, (state, action) => {
                state.isLoading = false
                state.token = action.payload.access_token
                state.refreshToken = action.payload.refresh_token
                state.isAuthenticated = true
            })
            .addCase(login.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            // Register
            .addCase(register.pending, (state) => {
                state.isLoading = true
                state.error = null
            })
            .addCase(register.fulfilled, (state) => {
                state.isLoading = false
            })
            .addCase(register.rejected, (state, action) => {
                state.isLoading = false
                state.error = action.payload as string
            })
            // Get Current User
            .addCase(getCurrentUser.fulfilled, (state, action) => {
                state.user = action.payload
                state.isAuthenticated = true
            })
    },
})

export const { logout, setToken, clearError } = authSlice.actions
export default authSlice.reducer
