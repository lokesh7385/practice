package com.example.livewallpapercountdown.service

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.os.Handler
import android.os.Looper
import android.service.wallpaper.WallpaperService
import android.view.SurfaceHolder
import com.example.livewallpapercountdown.data.PreferenceManager
import com.example.livewallpapercountdown.utils.TimeCalculator

class CountdownWallpaperService : WallpaperService() {

    override fun onCreateEngine(): Engine {
        return CountdownEngine()
    }

    inner class CountdownEngine : Engine() {
        private val handler = Handler(Looper.getMainLooper())
        private val drawRunner = Runnable { draw() }

        private var isVisible = false
        private val prefs = PreferenceManager(applicationContext)

        // Paint objects (Created once for performance)
        private val backgroundPaint = Paint().apply {
            color = Color.parseColor("#121212") // Dark Background
            style = Paint.Style.FILL
        }

        private val textPaint = Paint().apply {
            color = Color.WHITE
            textSize = 100f
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }

        private val titlePaint = Paint().apply {
            color = Color.LTGRAY
            textSize = 60f
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
        }

        override fun onVisibilityChanged(visible: Boolean) {
            this.isVisible = visible
            if (visible) {
                handler.post(drawRunner)
            } else {
                handler.removeCallbacks(drawRunner)
            }
        }

        override fun onSurfaceDestroyed(holder: SurfaceHolder?) {
            super.onSurfaceDestroyed(holder)
            this.isVisible = false
            handler.removeCallbacks(drawRunner)
        }

        override fun onSurfaceChanged(holder: SurfaceHolder?, format: Int, width: Int, height: Int) {
            super.onSurfaceChanged(holder, format, width, height)
            // Recalculate text size if needed based on width
            textPaint.textSize = width / 10f 
            titlePaint.textSize = width / 18f
            draw()
        }

        private fun draw() {
            val holder = surfaceHolder
            var canvas: Canvas? = null

            try {
                canvas = holder.lockCanvas()
                if (canvas != null) {
                    drawContent(canvas)
                }
            } finally {
                if (canvas != null) {
                    holder.unlockCanvasAndPost(canvas)
                }
            }

            // Schedule next frame
            handler.removeCallbacks(drawRunner)
            if (isVisible) {
                handler.postDelayed(drawRunner, 1000) // Update every 1 second
            }
        }

        private fun drawContent(canvas: Canvas) {
            // Draw Background
            canvas.drawRect(0f, 0f, canvas.width.toFloat(), canvas.height.toFloat(), backgroundPaint)

            // Get Data
            val title = prefs.getTitle()
            val targetDate = prefs.getTargetDate()
            val mode = prefs.getMode()
            val countdownText = TimeCalculator.calculate(mode, targetDate)

            // Draw Title
            val centerX = canvas.width / 2f
            val centerY = canvas.height / 2f
            
            canvas.drawText(title, centerX, centerY - 100, titlePaint)
            
            // Draw Countdown
            canvas.drawText(countdownText, centerX, centerY + 50, textPaint)
        }
    }
}
