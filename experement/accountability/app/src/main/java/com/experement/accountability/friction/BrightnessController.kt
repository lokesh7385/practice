package com.experement.accountability.friction

import android.content.Context
import android.provider.Settings

class BrightnessController(private val context: Context) {

    private var savedBrightness: Int = 128
    private var savedAutoMode: Int = 0

    // Requires: WRITE_SETTINGS permission (granted via system settings UI)

    fun setMinimum() {
        try {
            // Save current state
            savedAutoMode = Settings.System.getInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS_MODE,
                Settings.System.SCREEN_BRIGHTNESS_MODE_AUTOMATIC
            )
            savedBrightness = Settings.System.getInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS,
                128
            )

            // Disable auto-brightness, then drop to ~1%
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS_MODE,
                Settings.System.SCREEN_BRIGHTNESS_MODE_MANUAL
            )
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS,
                2  // 0-255 scale; 2 ≈ 1%
            )
        } catch (e: Exception) {}
    }

    fun restoreDefault() {
        try {
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS_MODE,
                savedAutoMode
            )
            Settings.System.putInt(
                context.contentResolver,
                Settings.System.SCREEN_BRIGHTNESS,
                savedBrightness
            )
        } catch (e: Exception) {}
    }
}
