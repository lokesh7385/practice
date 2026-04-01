package com.experement.accountability.friction

import android.content.Context
import android.provider.Settings

class GrayscaleController(private val context: Context) {

    // Requires: WRITE_SECURE_SETTINGS (granted via ADB)
    // Uses the "Simulate color space" developer option internally

    fun enable() {
        try {
            // 0 = Disabled, 2 = Monochromacy (grayscale)
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer_enabled",
                1
            )
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer",
                0  // 0 = Grayscale (monochromacy)
            )
        } catch (e: Exception) {}
    }

    fun disable() {
        try {
            Settings.Secure.putInt(
                context.contentResolver,
                "accessibility_display_daltonizer_enabled",
                0
            )
        } catch (e: Exception) {}
    }
}
