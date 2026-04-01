package com.experement.accountability.friction

import android.content.Context
import android.provider.Settings

class RefreshRateController(private val context: Context) {

    // Requires: WRITE_SECURE_SETTINGS (granted via ADB)
    // Moto G54 supports: 120Hz, 60Hz, 30Hz (display-dependent)

    fun setLow() {
        try {
            Settings.Secure.putFloat(
                context.contentResolver,
                "peak_refresh_rate",   // Cap max refresh rate
                30f
            )
            Settings.Secure.putFloat(
                context.contentResolver,
                "min_refresh_rate",
                30f
            )
        } catch (e: Exception) {
            // Fallback for some Moto builds if 30f fails
            Settings.Secure.putFloat(context.contentResolver, "peak_refresh_rate", 60f)
        }
    }

    fun restoreDefault() {
        try {
            Settings.Secure.putFloat(
                context.contentResolver,
                "peak_refresh_rate",
                120f
            )
            Settings.Secure.putFloat(
                context.contentResolver,
                "min_refresh_rate",
                60f
            )
        } catch (e: Exception) {}
    }
}
