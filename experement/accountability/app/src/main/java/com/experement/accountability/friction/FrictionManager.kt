package com.experement.accountability.friction

import android.content.Context

class FrictionManager(private val context: Context) {

    private val refreshRate = RefreshRateController(context)
    private val brightness = BrightnessController(context)
    private val grayscale = GrayscaleController(context)

    fun applyAllFriction() {
        val prefs = com.experement.accountability.data.GatekeeperPrefs(context)
        if (prefs.isGuestModeActive()) return

        refreshRate.setLow()       // 30Hz or 24Hz
        brightness.setMinimum()    // 1% brightness
        grayscale.enable()         // Full desaturation
    }

    fun removeAllFriction() {
        refreshRate.restoreDefault()
        brightness.restoreDefault()
        grayscale.disable()
    }
}
