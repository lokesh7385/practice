package com.experement.accountability.data

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.experement.accountability.util.PackageUtils.isAccessibilityServiceEnabled
import com.experement.accountability.service.GatekeeperAccessibilityService

class ServiceCheckWorker(
    private val appContext: Context,
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val isEnabled = isAccessibilityServiceEnabled(appContext, GatekeeperAccessibilityService::class.java)
        
        if (!isEnabled) {
            // TODO: In a real app we'd fire a sticky notification here
            // nagging the user to re-enable the accessibility service.
        }
        
        return Result.success()
    }
}
