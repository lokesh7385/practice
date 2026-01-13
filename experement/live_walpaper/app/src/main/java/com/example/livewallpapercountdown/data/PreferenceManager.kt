package com.example.livewallpapercountdown.data

import android.content.Context
import android.content.SharedPreferences
import com.example.livewallpapercountdown.utils.CountdownMode
import java.time.LocalDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

class PreferenceManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun saveTargetDate(date: LocalDateTime) {
        prefs.edit().putString(KEY_TARGET_DATE, date.format(formatter)).apply()
    }

    fun getTargetDate(): LocalDateTime {
        val dateString = prefs.getString(KEY_TARGET_DATE, null)
        return if (dateString != null) {
            try {
                LocalDateTime.parse(dateString, formatter)
            } catch (e: Exception) {
                defaultTargetDate()
            }
        } else {
            defaultTargetDate()
        }
    }

    fun saveTitle(title: String) {
        prefs.edit().putString(KEY_TITLE, title).apply()
    }

    fun getTitle(): String {
        return prefs.getString(KEY_TITLE, "My Event") ?: "My Event"
    }

    fun saveMode(mode: CountdownMode) {
        prefs.edit().putString(KEY_MODE, mode.name).apply()
    }

    fun getMode(): CountdownMode {
        val modeName = prefs.getString(KEY_MODE, CountdownMode.FULL_COUNTDOWN.name)
        return try {
            CountdownMode.valueOf(modeName ?: CountdownMode.FULL_COUNTDOWN.name)
        } catch (e: IllegalArgumentException) {
            CountdownMode.FULL_COUNTDOWN
        }
    }

    private fun defaultTargetDate(): LocalDateTime {
        // Default to New Year of next year
        return LocalDateTime.now().plusYears(1).withDayOfYear(1).withHour(0).withMinute(0).withSecond(0)
    }

    companion object {
        private const val PREFS_NAME = "live_wallpaper_prefs"
        private const val KEY_TARGET_DATE = "target_date"
        private const val KEY_TITLE = "title"
        private const val KEY_MODE = "mode"
        
        private val formatter = DateTimeFormatter.ISO_LOCAL_DATE_TIME
    }
}
