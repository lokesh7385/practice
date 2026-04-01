package com.example.livewallpapercountdown.service

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.os.Handler
import android.os.Looper
import android.service.wallpaper.WallpaperService
import android.view.SurfaceHolder
import com.example.livewallpapercountdown.engine.YearProgressEngine
import com.example.livewallpapercountdown.model.DayState
import com.example.livewallpapercountdown.model.DayStatus

class YearProgressWallpaperService : WallpaperService() {

    override fun onCreateEngine(): Engine {
        return YearProgressEngineWrapper()
    }

    inner class YearProgressEngineWrapper : Engine() {
        private val handler = Handler(Looper.getMainLooper())
        private val drawRunner = Runnable { draw() }

        private var isVisible = false
        
        // Engine
        private val engine = YearProgressEngine()
        private var yearData: List<DayState> = emptyList()

        // Paints
        private val backgroundPaint = Paint().apply {
            color = Color.parseColor("#121212") // Dark Background
            style = Paint.Style.FILL
        }

        private val pastDotPaint = Paint().apply {
            color = Color.WHITE
            style = Paint.Style.FILL
            isAntiAlias = true
        }

        private val todayDotPaint = Paint().apply {
            color = Color.parseColor("#FF9800") // Orange
            style = Paint.Style.FILL
            isAntiAlias = true
        }

        private val futureDotPaint = Paint().apply {
            color = Color.DKGRAY
            style = Paint.Style.FILL
            isAntiAlias = true
        }

        private val textPaint = Paint().apply {
            color = Color.WHITE
            textSize = 50f
            textAlign = Paint.Align.CENTER
            isAntiAlias = true
            isFakeBoldText = true // Bold text
        }

        override fun onCreate(surfaceHolder: SurfaceHolder?) {
            super.onCreate(surfaceHolder)
            // Initial data load
            yearData = engine.getYearData()
        }

        override fun onVisibilityChanged(visible: Boolean) {
            this.isVisible = visible
            if (visible) {
                 // Refresh data when becoming visible to ensure day change is caught
                yearData = engine.getYearData()
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
            draw()
        }

        private fun draw() {
            // ... existing draw structure ...
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
                // Update every second for the timer
                handler.postDelayed(drawRunner, 1000)
            }
        }

        private fun drawContent(canvas: Canvas) {
            val width = canvas.width.toFloat()
            val height = canvas.height.toFloat()

            // 1. Background
            canvas.drawRect(0f, 0f, width, height, backgroundPaint)

            // 2. Dots Grid
            val cols = 15
            // Dynamic rows calculation to fit exactly the needed dots
            val totalDots = yearData.size
            val rows = kotlin.math.ceil(totalDots.toDouble() / cols).toInt()

            val margin = 50f
            val availableWidth = width - (2 * margin)
            
            // Calculate sizes
            // width = cols * 2R + (cols - 1) * spacing
            // Spacing = dotRadius
            val dotRadius = availableWidth / (3 * cols - 1)
            val spacing = dotRadius
            
            val gridWidth = (cols * 2 * dotRadius) + ((cols - 1) * spacing)
            val gridHeight = (rows * 2 * dotRadius) + ((rows - 1) * spacing)

            // Center Grid
            val gridCenterX = width / 2
            val gridCenterY = height / 2 // Center vertically
            
            val startX = gridCenterX - (gridWidth / 2) + dotRadius
            val startY = gridCenterY - (gridHeight / 2) + dotRadius
            
            var currentX = startX
            var currentY = startY

            var colCounter = 0

            for (dayState in yearData) {
                val paint = when (dayState.status) {
                    DayStatus.PAST -> pastDotPaint
                    DayStatus.TODAY -> todayDotPaint
                    DayStatus.FUTURE -> futureDotPaint
                }

                canvas.drawCircle(currentX, currentY, dotRadius, paint)

                colCounter++
                if (colCounter >= cols) {
                    colCounter = 0
                    currentX = startX
                    currentY += (dotRadius * 2) + spacing
                } else {
                    currentX += (dotRadius * 2) + spacing
                }
            }
            
            // 3. Timer Text (Upper Center - adjusted relative to grid or screen)
            // Let's keep it somewhat above the grid, or just fixed at top?
            // User asked for "Upper Center". Let's stick to 15-20% height or use margin.
            val daysLeft = yearData.count { it.status == DayStatus.FUTURE }
            val timeString = engine.getFormattedTimeRemaining()
            val text = "$daysLeft days left • $timeString"

            // Ensure timer doesn't overlap if screen is short? 
            // 20% height is usually safe. 
            val textY = height * 0.15f 
            canvas.drawText(text, width / 2, textY, textPaint)
        }
    }
}
