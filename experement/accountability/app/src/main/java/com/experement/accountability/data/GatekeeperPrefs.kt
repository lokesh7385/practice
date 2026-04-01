package com.experement.accountability.data

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.longPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.runBlocking

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "gatekeeper_prefs")

class GatekeeperPrefs(private val context: Context) {
    private val IN_GUEST_MODE = booleanPreferencesKey("in_guest_mode")
    private val GUEST_MODE_EXPIRY = longPreferencesKey("guest_mode_expiry")

    fun activateGuestMode(durationMinutes: Int) {
        val expiry = System.currentTimeMillis() + (durationMinutes * 60 * 1000)
        runBlocking {
            context.dataStore.edit { prefs ->
                prefs[IN_GUEST_MODE] = true
                prefs[GUEST_MODE_EXPIRY] = expiry
            }
        }
    }

    fun deactivateGuestMode() {
        runBlocking {
            context.dataStore.edit { prefs ->
                prefs[IN_GUEST_MODE] = false
                prefs[GUEST_MODE_EXPIRY] = 0L
            }
        }
    }

    fun isGuestModeActive(): Boolean {
        return runBlocking {
            val flow = context.dataStore.data.map { prefs ->
                val isActive = prefs[IN_GUEST_MODE] ?: false
                val expiry = prefs[GUEST_MODE_EXPIRY] ?: 0L
                isActive && System.currentTimeMillis() < expiry
            }
            flow.first()
        }
    }
}
