package com.experement.accountability.ai

sealed class AiVerdict {
    data class Approved(val reason: String, val timeLimitMinutes: Int) : AiVerdict()
    data class Denied(val reason: String) : AiVerdict()
    data object Timeout : AiVerdict()
}
