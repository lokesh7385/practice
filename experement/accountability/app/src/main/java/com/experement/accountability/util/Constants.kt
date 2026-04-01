package com.experement.accountability.util

object Constants {
    // Defines apps that trigger the gatekeeper when opened
    val DEFAULT_GATED_PACKAGES = setOf(
        "com.instagram.android",
        "com.google.android.youtube",
        "com.zhiliaoapp.musically",   // TikTok
        "com.twitter.android",
        "com.reddit.frontpage",
        "com.facebook.katana"         // Facebook
    )

    const val OVERLAY_TIMEOUT_MS = 30000L // 30 sec to answer AI
    const val GUEST_MODE_MAX_DURATION_MINUTES = 30
}
