package com.finbuddy.connector.sync

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.finbuddy.connector.data.model.ParsedTransactionData
import com.finbuddy.connector.data.model.SmsMessage
import com.finbuddy.connector.data.model.SmsTransactionRequest
import com.finbuddy.connector.data.remote.ApiService
import com.finbuddy.connector.data.repository.SmsRepository
import com.finbuddy.connector.sms.SmsParser
import com.finbuddy.connector.utils.Result
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

@HiltWorker
class SmsSyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val smsRepository: SmsRepository,
    private val apiService: ApiService
) : CoroutineWorker(context, workerParams) {

    companion object {
        const val PERIODIC_WORK_NAME = "sms_sync_periodic"
        const val KEY_SMS_SENDER = "sms_sender"
        const val KEY_SMS_BODY = "sms_body"
        const val KEY_SMS_TIMESTAMP = "sms_timestamp"
        const val KEY_IMMEDIATE_SYNC = "immediate_sync"
    }

    private val smsParser = SmsParser()

    override suspend fun doWork(): Result {
        val isImmediate = inputData.getBoolean(KEY_IMMEDIATE_SYNC, false)

        return if (isImmediate) {
            handleImmediateSync()
        } else {
            handlePeriodicSync()
        }
    }

    private suspend fun handleImmediateSync(): Result {
        val sender = inputData.getString(KEY_SMS_SENDER) ?: return Result.failure()
        val body = inputData.getString(KEY_SMS_BODY) ?: return Result.failure()
        val timestamp = inputData.getLong(KEY_SMS_TIMESTAMP, 0L)

        if (timestamp == 0L) return Result.failure()

        val smsMessage = SmsMessage(
            id = timestamp, // Using timestamp as ID for immediate messages
            sender = sender,
            body = body,
            timestamp = timestamp,
            isRead = false
        )

        val parsedTransaction = smsParser.parseSms(smsMessage)
        
        if (!parsedTransaction.isFinancialSms) {
            return Result.success()
        }

        return try {
            val request = SmsTransactionRequest(
                smsBody = body,
                sender = sender,
                timestamp = timestamp,
                parsedData = ParsedTransactionData(
                    amount = parsedTransaction.amount,
                    transactionType = parsedTransaction.transactionType?.value, // Use .value for enum
                    category = parsedTransaction.category.value, // Added category
                    merchant = parsedTransaction.merchant,
                    accountNumber = parsedTransaction.accountNumber,
                    bankName = parsedTransaction.bankName,
                    balance = parsedTransaction.balance,
                    referenceNumber = parsedTransaction.referenceNumber,
                    transactionDate = null
                )
            )

            val response = apiService.uploadTransactions(request)
            if (response.isSuccessful) {
                Result.success()
            } else {
                Result.retry()
            }
        } catch (e: Exception) {
            Result.retry()
        }
    }

    private suspend fun handlePeriodicSync(): Result {
        return when (val result = smsRepository.performFullSync()) {
            is com.finbuddy.connector.utils.Result.Success -> Result.success()
            is com.finbuddy.connector.utils.Result.Error -> Result.retry()
        }
    }
}
