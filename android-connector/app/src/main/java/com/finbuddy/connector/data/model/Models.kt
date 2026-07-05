package com.finbuddy.connector.data.model

import com.google.gson.annotations.SerializedName

// ==================== AUTH MODELS ====================

data class LoginRequest(
    val email: String,
    val password: String
)

/**
 * Login response matches backend TokenResponse
 * Backend: access_token, refresh_token, token_type
 */
data class LoginResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type") val tokenType: String = "bearer"
)

data class RefreshTokenRequest(
    @SerializedName("refresh_token") val refreshToken: String
)

data class TokenResponse(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("refresh_token") val refreshToken: String,
    @SerializedName("token_type") val tokenType: String = "bearer"
)

/**
 * User response from /users/me endpoint
 */
data class UserResponse(
    val id: String,
    val email: String,
    @SerializedName("full_name") val fullName: String?,
    val phone: String?,
    @SerializedName("avatar_url") val avatarUrl: String?,
    @SerializedName("monthly_income") val monthlyIncome: Double?,
    @SerializedName("risk_tolerance") val riskTolerance: String?,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("is_verified") val isVerified: Boolean
)

// ==================== TRANSACTION MODELS (Matching Backend) ====================

/**
 * Transaction types matching backend TransactionType enum
 */
enum class TransactionType(val value: String) {
    CREDIT("credit"),
    DEBIT("debit");
    
    companion object {
        fun fromString(value: String?): TransactionType {
            return when (value?.lowercase()) {
                "credit" -> CREDIT
                "debit" -> DEBIT
                else -> DEBIT
            }
        }
    }
}

/**
 * Transaction categories matching backend TransactionCategory enum
 */
enum class TransactionCategory(val value: String) {
    NEEDS("needs"),
    ESSENTIALS("essentials"),
    SPENDS("spends"),
    BILLS("bills"),
    SAVINGS("savings"),
    INVESTMENTS("investments"),
    INCOME("income"),
    TRANSFER("transfer"),
    OTHER("other");
    
    companion object {
        fun fromString(value: String?): TransactionCategory {
            return entries.find { it.value == value?.lowercase() } ?: OTHER
        }
    }
}

/**
 * Transaction source matching backend TransactionSource enum
 */
enum class TransactionSource(val value: String) {
    MANUAL("manual"),
    SMS("sms"),
    BANK_STATEMENT("bank_statement"),
    RECEIPT("receipt"),
    BANK_API("bank_api")
}

// ==================== SMS TRANSACTION REQUEST/RESPONSE ====================

/**
 * Parsed data from SMS - sent to backend
 */
data class ParsedTransactionData(
    val amount: Double?,
    @SerializedName("transaction_type") val transactionType: String?,
    val category: String?,  // Added: category matching backend
    val merchant: String?,
    @SerializedName("account_number") val accountNumber: String?,
    @SerializedName("bank_name") val bankName: String?,
    val balance: Double?,
    @SerializedName("reference_number") val referenceNumber: String?,
    @SerializedName("transaction_date") val transactionDate: String?
)

/**
 * Single SMS transaction upload request
 */
data class SmsTransactionRequest(
    @SerializedName("sms_body") val smsBody: String,
    val sender: String,
    val timestamp: Long,
    @SerializedName("parsed_data") val parsedData: ParsedTransactionData?
)

/**
 * Response for single SMS transaction
 */
data class SmsTransactionResponse(
    val id: String,
    val status: String,
    val message: String
)

/**
 * Response for batch SMS transaction upload
 * Matches backend BatchTransactionResponse exactly
 */
data class BatchTransactionResponse(
    @SerializedName("total_received") val totalReceived: Int = 0,
    @SerializedName("total_processed") val totalProcessed: Int = 0,
    @SerializedName("total_failed") val totalFailed: Int = 0,
    @SerializedName("total_duplicates") val totalDuplicates: Int = 0,
    @SerializedName("transaction_ids") val transactionIds: List<String> = emptyList()
)

/**
 * Sync status response
 */
data class SyncStatusResponse(
    @SerializedName("last_sync") val lastSync: Long?,
    @SerializedName("pending_count") val pendingCount: Int,
    @SerializedName("total_synced") val totalSynced: Int
)

/**
 * Sync completion notification
 */
data class SyncCompleteRequest(
    @SerializedName("sync_timestamp") val syncTimestamp: Long,
    @SerializedName("transactions_count") val transactionsCount: Int
)

// ==================== LOCAL SMS MODELS ====================

/**
 * Local SMS message from device
 */
data class SmsMessage(
    val id: Long,
    val sender: String,
    val body: String,
    val timestamp: Long,
    val isRead: Boolean
)

/**
 * Parsed transaction from SMS
 */
data class ParsedTransaction(
    val originalSms: SmsMessage,
    val amount: Double?,
    val transactionType: TransactionType?,
    val merchant: String?,
    val accountNumber: String?,
    val bankName: String?,
    val balance: Double?,
    val referenceNumber: String?,
    val category: TransactionCategory,
    val isFinancialSms: Boolean
)

// ==================== SYNC STATUS ====================

data class SyncStats(
    val totalSmsRead: Int = 0,
    val financialSmsFound: Int = 0,
    val transactionsUploaded: Int = 0,
    val duplicatesSkipped: Int = 0,
    val failedUploads: Int = 0,
    val lastSyncTime: Long = 0
)
