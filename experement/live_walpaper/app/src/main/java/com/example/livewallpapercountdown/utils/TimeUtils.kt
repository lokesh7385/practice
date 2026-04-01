package com.example.livewallpapercountdown.utils

import java.time.LocalDate
import java.time.LocalTime
import java.time.Year
import java.time.temporal.ChronoUnit

object TimeUtils {

    fun getDaysInCurrentYear(): Int {
        return Year.now().length()
    }

    fun getCurrentDayOfYear(): Int {
        return LocalDate.now().dayOfYear
    }

    /**
     * Returns the seconds remaining until midnight (end of the current day).
     */
    fun getSecondsRemainingInDay(): Long {
        val now = LocalTime.now()
        val midnight = LocalTime.MAX
        return ChronoUnit.SECONDS.between(now, midnight)
    }

    /**
     * Formats seconds into HH:MM:SS.
     */
    fun formatSecondsToTimer(seconds: Long): String {
        val hrs = seconds / 3600
        val mins = (seconds % 3600) / 60
        val secs = seconds % 60
        return String.format("%02d:%02d:%02d", hrs, mins, secs)
    }
}
