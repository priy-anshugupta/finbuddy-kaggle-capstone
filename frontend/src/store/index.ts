import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import dashboardReducer from './slices/dashboardSlice'
import chatReducer from './slices/chatSlice'
import transactionsReducer from './slices/transactionsSlice'
import investmentsReducer from './slices/investmentsSlice'

export const store = configureStore({
    reducer: {
        auth: authReducer,
        dashboard: dashboardReducer,
        chat: chatReducer,
        transactions: transactionsReducer,
        investments: investmentsReducer,
    },
    middleware: (getDefaultMiddleware) =>
        getDefaultMiddleware({
            serializableCheck: false,
        }),
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
