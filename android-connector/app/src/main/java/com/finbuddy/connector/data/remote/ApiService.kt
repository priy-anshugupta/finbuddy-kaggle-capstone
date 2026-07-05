package com.finbuddy.connector.data.remote

import com.finbuddy.connector.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // Authentication
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<TokenResponse>

    @GET("users/me")
    suspend fun getCurrentUser(): Response<UserResponse>

    // SMS Transactions
    @POST("sms/transactions")
    suspend fun uploadTransactions(@Body request: SmsTransactionRequest): Response<SmsTransactionResponse>

    @POST("sms/transactions/batch")
    suspend fun uploadTransactionsBatch(@Body request: List<SmsTransactionRequest>): Response<BatchTransactionResponse>

    @GET("sms/sync-status")
    suspend fun getSyncStatus(): Response<SyncStatusResponse>

    @POST("sms/sync-complete")
    suspend fun markSyncComplete(@Body request: SyncCompleteRequest): Response<Unit>
}
