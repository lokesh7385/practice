package com.experement.accountability.service

import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import com.experement.accountability.data.GatekeeperPrefs

class GuestModeTileService : TileService() {

    override fun onClick() {
        val tile = qsTile ?: return

        val prefs = GatekeeperPrefs(applicationContext)
        val isActive = prefs.isGuestModeActive()

        if (isActive) {
            prefs.deactivateGuestMode()
            tile.state = Tile.STATE_INACTIVE
            tile.label = "Guest Mode"
            tile.subtitle = "OFF"
        } else {
            prefs.activateGuestMode(durationMinutes = 30)
            tile.state = Tile.STATE_ACTIVE
            tile.label = "Guest Mode"
            tile.subtitle = "30 min"
        }
        tile.updateTile()
    }

    override fun onStartListening() {
        val tile = qsTile ?: return
        val prefs = GatekeeperPrefs(applicationContext)
        if (prefs.isGuestModeActive()) {
            tile.state = Tile.STATE_ACTIVE
            tile.label = "Guest Mode"
            tile.subtitle = "Running"
        } else {
            tile.state = Tile.STATE_INACTIVE
            tile.label = "Guest Mode"
            tile.subtitle = "OFF"
        }
        tile.updateTile()
    }
}
