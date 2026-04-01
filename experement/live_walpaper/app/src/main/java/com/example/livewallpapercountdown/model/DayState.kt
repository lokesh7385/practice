package com.example.livewallpapercountdown.model

enum class DayStatus {
    PAST,
    TODAY,
    FUTURE
}

data class DayState(
    val dayOfYear: Int,
    val status: DayStatus
)
