package com.example.livewallpapercountdown.utils

/**
 * Defines the different display modes for the live wallpaper.
 *
 * @property displayName User-friendly name for UI selectors.
 */
enum class CountdownMode(val displayName: String) {
    FULL_COUNTDOWN("Full Countdown (D : H : M : S)"),
    SECONDS_TODAY("Seconds Left in Today"),
    MINUTES_TODAY("Minutes Left in Today");

    // Future modes: SECONDS_WEEK, DAYS_YEAR, etc.
}
