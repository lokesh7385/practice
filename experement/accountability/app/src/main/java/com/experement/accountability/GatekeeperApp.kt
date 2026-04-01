package com.experement.accountability

import android.app.Application
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.experement.accountability.data.ServiceCheckWorker
import dagger.hilt.android.HiltAndroidApp
import java.util.concurrent.TimeUnit

@HiltAndroidApp
class GatekeeperApp : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // Anti-cheat: Check every 15 minutes if the service is still enabled
        val workRequest = PeriodicWorkRequestBuilder<ServiceCheckWorker>(
            15, TimeUnit.MINUTES
        ).build()
            
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "service_check",
            ExistingPeriodicWorkPolicy.KEEP,
            workRequest
        )
    }
}
