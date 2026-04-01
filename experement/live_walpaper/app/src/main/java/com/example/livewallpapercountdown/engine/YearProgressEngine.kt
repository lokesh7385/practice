package com.example.livewallpapercountdown.engine

import com.example.livewallpapercountdown.model.DayState
import com.example.livewallpapercountdown.model.DayStatus
import com.example.livewallpapercountdown.utils.TimeUtils

class YearProgressEngine {

    fun getYearData(): List<DayState> {
        val daysInYear = TimeUtils.getDaysInCurrentYear()
        val currentDay = TimeUtils.getCurrentDayOfYear()

        val dayStates = ArrayList<DayState>(daysInYear)

        for (i in 1..daysInYear) {
            val status = when {
                i < currentDay -> DayStatus.PAST
                i == currentDay -> DayStatus.TODAY
                else -> DayStatus.FUTURE
            }
            dayStates.add(DayState(i, status))
        }
        return dayStates
    }

    fun getSecondsRemainingInDay(): Long {
        return TimeUtils.getSecondsRemainingInDay()
    }
    
    fun getFormattedTimeRemaining(): String {
        return TimeUtils.formatSecondsToTimer(getSecondsRemainingInDay())    
    }
}
