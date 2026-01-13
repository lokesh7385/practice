package com.example.livewallpapercountdown.utils

import java.time.Duration
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.temporal.ChronoUnit

/**
 * Centralized logic for all time calculations.
 * Ensures the WallpaperService is mode-agnostic.
 */
object TimeCalculator {

    /**
     * Calculates the display string based on the selected mode.
     *
     * @param mode The selected CountdownMode.
     * @param target The user-defined target date/time (used for FULL_COUNTDOWN).
     * @return Formatted string to display.
     */
    fun calculate(mode: CountdownMode, target: LocalDateTime): String {
        val now = LocalDateTime.now()

        return when (mode) {
            CountdownMode.FULL_COUNTDOWN -> calculateFullCountdown(now, target)
            CountdownMode.SECONDS_TODAY -> calculateSecondsRemainingToday(now)
            CountdownMode.MINUTES_TODAY -> calculateMinutesRemainingToday(now)
        }
    }

    private fun calculateFullCountdown(now: LocalDateTime, target: LocalDateTime): String {
        if (now.isAfter(target)) return "00 : 00 : 00 : 00"

        val duration = Duration.between(now, target)
        
        // Manual calculation for better compatibility across API levels < 31
        val days = duration.toDays()
        val hours = duration.toHours() % 24
        val minutes = duration.toMinutes() % 60
        val seconds = duration.seconds % 60

        return "%02d : %02d : %02d : %02d".format(days, hours, minutes, seconds)
    }

    private fun calculateSecondsRemainingToday(now: LocalDateTime): String {
        val endOfDay = now.toLocalDate().atTime(LocalTime.MAX)
        val seconds = ChronoUnit.SECONDS.between(now, endOfDay)
        return seconds.toString()
    }

    private fun calculateMinutesRemainingToday(now: LocalDateTime): String {
        val endOfDay = now.toLocalDate().atTime(LocalTime.MAX)
        val minutes = ChronoUnit.MINUTES.between(now, endOfDay)
        return minutes.toString()
    }
}
