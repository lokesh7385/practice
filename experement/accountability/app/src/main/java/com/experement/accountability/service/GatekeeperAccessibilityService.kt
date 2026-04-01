package com.experement.accountability.service

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.view.accessibility.AccessibilityEvent
import com.experement.accountability.data.SessionState
import com.experement.accountability.util.Constants

class GatekeeperAccessibilityService : AccessibilityService() {

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return

        val pkg = event.packageName?.toString() ?: return

        // Ignore self and system UI
        if (pkg == packageName || pkg == "com.android.systemui") return

        if (pkg in Constants.DEFAULT_GATED_PACKAGES && !SessionState.isCurrentlyApproved(pkg)) {
            // Launch overlay via ForegroundService
            val intent = Intent(this, OverlayService::class.java).apply {
                putExtra("target_package", pkg)
            }
            startForegroundService(intent)

            // Force user back to home (buys time for overlay)
            performGlobalAction(GLOBAL_ACTION_HOME)
        }
    }

    override fun onInterrupt() {
        val frictionManager = com.experement.accountability.friction.FrictionManager(this)
        frictionManager.removeAllFriction()
    }

    override fun onDestroy() {
        super.onDestroy()
        val frictionManager = com.experement.accountability.friction.FrictionManager(this)
        frictionManager.removeAllFriction()
    }
}
