package com.finbuddy.connector.sms

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.finbuddy.connector.sync.SmsSyncWorker
import java.util.concurrent.TimeUnit

class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Schedule periodic sync after boot
            schedulePeriodicSync(context)
        }
    }

    private fun schedulePeriodicSync(context: Context) {
        val periodicWork = PeriodicWorkRequestBuilder<SmsSyncWorker>(
            6, TimeUnit.HOURS,
            15, TimeUnit.MINUTES
        ).build()

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            SmsSyncWorker.PERIODIC_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            periodicWork
        )
    }
}
