package com.experement.accountability.data

object SessionState {
    // Basic in-memory map of approved packages and their expiry time (epoch millis)
    private val approvedPackages = mutableMapOf<String, Long>()

    fun approveApp(packageName: String, durationMinutes: Int) {
        approvedPackages[packageName] = System.currentTimeMillis() + (durationMinutes * 60 * 1000)
    }

    fun isCurrentlyApproved(packageName: String): Boolean {
        val expiry = approvedPackages[packageName] ?: return false
        return if (System.currentTimeMillis() < expiry) {
            true
        } else {
            // Cleanup expired
            approvedPackages.remove(packageName)
            false
        }
    }
}
