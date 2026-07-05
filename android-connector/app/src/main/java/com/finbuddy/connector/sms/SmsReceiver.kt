package com.finbuddy.connector.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.workDataOf
import com.finbuddy.connector.sync.SmsSyncWorker
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class SmsReceiver : BroadcastReceiver() {

    private val smsParser = SmsParser()

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) {
            return
        }

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
        
        messages?.forEach { smsMessage ->
            val sender = smsMessage.displayOriginatingAddress ?: return@forEach
            val body = smsMessage.messageBody ?: return@forEach
            val timestamp = smsMessage.timestampMillis

            // Check if it's from a financial sender
            if (smsParser.isFinancialSender(sender)) {
                // Trigger immediate sync for this SMS
                scheduleImmediateSync(context, sender, body, timestamp)
            }
        }
    }

    private fun scheduleImmediateSync(
        context: Context,
        sender: String,
        body: String,
        timestamp: Long
    ) {
        val workRequest = OneTimeWorkRequestBuilder<SmsSyncWorker>()
            .setInputData(
                workDataOf(
                    SmsSyncWorker.KEY_SMS_SENDER to sender,
                    SmsSyncWorker.KEY_SMS_BODY to body,
                    SmsSyncWorker.KEY_SMS_TIMESTAMP to timestamp,
                    SmsSyncWorker.KEY_IMMEDIATE_SYNC to true
                )
            )
            .build()

        WorkManager.getInstance(context).enqueue(workRequest)
    }
}
