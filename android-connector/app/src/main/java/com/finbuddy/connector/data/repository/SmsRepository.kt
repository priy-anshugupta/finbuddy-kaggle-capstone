package com.finbuddy.connector.data.repository

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.provider.Telephony
import android.util.Log
import androidx.core.content.ContextCompat
import com.finbuddy.connector.data.local.PreferencesManager
import com.finbuddy.connector.data.model.*
import com.finbuddy.connector.data.remote.ApiService
import com.finbuddy.connector.sms.SmsParser
import com.finbuddy.connector.utils.Result
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SmsRepository @Inject constructor(
    private val context: Context,
    private val apiService: ApiService,
    private val preferencesManager: PreferencesManager
) {
    private val smsParser = SmsParser()
    private val dateFormatter = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.US)
    
    companion object {
        private const val TAG = "SmsRepository"
    }

    suspend fun readAllFinancialSms(
        sinceTimestamp: Long = 0
    ): Result<List<ParsedTransaction>> = withContext(Dispatchers.IO) {
        if (!hasSmsPermission()) {
            return@withContext Result.Error(Exception("SMS permission not granted"))
        }

        try {
            val smsList = readSmsFromDevice(sinceTimestamp)
            Log.d(TAG, "Read ${smsList.size} SMS messages from device")
            
            val parsedTransactions = smsList
                .map { sms -> smsParser.parseSms(sms) }
                .filter { it.isFinancialSms && it.amount != null }

            Log.d(TAG, "Parsed ${parsedTransactions.size} financial transactions")
            Result.Success(parsedTransactions)
        } catch (e: Exception) {
            Log.e(TAG, "Error reading SMS", e)
            Result.Error(e)
        }
    }

    private fun hasSmsPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.READ_SMS
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun readSmsFromDevice(sinceTimestamp: Long): List<SmsMessage> {
        val smsList = mutableListOf<SmsMessage>()
        val uri: Uri = Telephony.Sms.Inbox.CONTENT_URI

        val projection = arrayOf(
            Telephony.Sms._ID,
            Telephony.Sms.ADDRESS,
            Telephony.Sms.BODY,
            Telephony.Sms.DATE,
            Telephony.Sms.READ
        )

        val selection = if (sinceTimestamp > 0) {
            "${Telephony.Sms.DATE} > ?"
        } else null

        val selectionArgs = if (sinceTimestamp > 0) {
            arrayOf(sinceTimestamp.toString())
        } else null

        val sortOrder = "${Telephony.Sms.DATE} DESC"

        val cursor: Cursor? = context.contentResolver.query(
            uri,
            projection,
            selection,
            selectionArgs,
            sortOrder
        )

        cursor?.use {
            val idIndex = it.getColumnIndexOrThrow(Telephony.Sms._ID)
            val addressIndex = it.getColumnIndexOrThrow(Telephony.Sms.ADDRESS)
            val bodyIndex = it.getColumnIndexOrThrow(Telephony.Sms.BODY)
            val dateIndex = it.getColumnIndexOrThrow(Telephony.Sms.DATE)
            val readIndex = it.getColumnIndexOrThrow(Telephony.Sms.READ)

            while (it.moveToNext()) {
                val sender = it.getString(addressIndex) ?: ""
                
                // Filter for bank/financial SMS senders
                if (smsParser.isFinancialSender(sender)) {
                    smsList.add(
                        SmsMessage(
                            id = it.getLong(idIndex),
                            sender = sender,
                            body = it.getString(bodyIndex) ?: "",
                            timestamp = it.getLong(dateIndex),
                            isRead = it.getInt(readIndex) == 1
                        )
                    )
                }
            }
        }

        return smsList
    }

    /**
     * Sync transactions to server using the backend's expected format
     */
    suspend fun syncTransactionsToServer(
        transactions: List<ParsedTransaction>
    ): Result<BatchTransactionResponse> {
        return try {
            Log.d(TAG, "Syncing ${transactions.size} transactions to server")
            
            val requests = transactions.mapNotNull { parsed ->
                // Skip if amount is null
                if (parsed.amount == null) return@mapNotNull null
                
                // Format timestamp to ISO date string
                val transactionDate = dateFormatter.format(Date(parsed.originalSms.timestamp))
                
                SmsTransactionRequest(
                    smsBody = parsed.originalSms.body,
                    sender = parsed.originalSms.sender,
                    timestamp = parsed.originalSms.timestamp,
                    parsedData = ParsedTransactionData(
                        amount = parsed.amount,
                        transactionType = parsed.transactionType?.value, // Use .value for enum
                        category = parsed.category.value, // Use .value for enum
                        merchant = parsed.merchant,
                        accountNumber = parsed.accountNumber,
                        bankName = parsed.bankName,
                        balance = parsed.balance,
                        referenceNumber = parsed.referenceNumber,
                        transactionDate = transactionDate
                    )
                )
            }

            if (requests.isEmpty()) {
                Log.d(TAG, "No valid transactions to sync")
                return Result.Success(BatchTransactionResponse(
                    totalReceived = 0,
                    totalProcessed = 0,
                    totalFailed = 0,
                    totalDuplicates = 0,
                    transactionIds = emptyList()
                ))
            }

            Log.d(TAG, "Sending ${requests.size} transactions to API")
            val response = apiService.uploadTransactionsBatch(requests)
            
            if (response.isSuccessful && response.body() != null) {
                val syncTime = System.currentTimeMillis()
                preferencesManager.updateLastSyncTime(syncTime)
                Log.d(TAG, "Sync successful: ${response.body()}")
                Result.Success(response.body()!!)
            } else {
                val error = response.errorBody()?.string() ?: "Upload failed"
                Log.e(TAG, "Sync failed: $error")
                Result.Error(Exception(error))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Sync error", e)
            Result.Error(e)
        }
    }

    suspend fun getLastSyncTime(): Long {
        return preferencesManager.lastSyncTime.first()
    }

    suspend fun performFullSync(): Result<Int> {
        val lastSync = getLastSyncTime()
        
        return when (val smsResult = readAllFinancialSms(lastSync)) {
            is Result.Success -> {
                if (smsResult.data.isEmpty()) {
                    Result.Success(0)
                } else {
                    when (val uploadResult = syncTransactionsToServer(smsResult.data)) {
                        is Result.Success -> Result.Success(uploadResult.data.totalProcessed)
                        is Result.Error -> Result.Error(uploadResult.exception)
                    }
                }
            }
            is Result.Error -> Result.Error(smsResult.exception)
        }
    }
}
