package com.example.livewallpapercountdown.ui

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.app.WallpaperManager
import android.content.ComponentName
import android.content.Intent
import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.livewallpapercountdown.R
import com.example.livewallpapercountdown.data.PreferenceManager
import com.example.livewallpapercountdown.service.CountdownWallpaperService
import com.example.livewallpapercountdown.utils.CountdownMode
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

class MainActivity : AppCompatActivity() {

    private lateinit var prefs: PreferenceManager
    private lateinit var etTitle: EditText
    private lateinit var spinnerMode: Spinner
    private lateinit var tvDate: TextView
    private lateinit var tvTime: TextView

    private var selectedDate: LocalDateTime = LocalDateTime.now().plusDays(1)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = PreferenceManager(this)
        
        // Initialize Views
        etTitle = findViewById(R.id.etTitle)
        spinnerMode = findViewById(R.id.spinnerMode)
        tvDate = findViewById(R.id.tvDate)
        tvTime = findViewById(R.id.tvTime)
        
        val btnDate = findViewById<Button>(R.id.btnDate)
        val btnTime = findViewById<Button>(R.id.btnTime)
        val btnSave = findViewById<Button>(R.id.btnSave)

        // Setup Mode Spinner
        setupSpinner()

        // Load current values
        loadCurrentValues()

        // Listeners
        btnDate.setOnClickListener { showDatePicker() }
        btnTime.setOnClickListener { showTimePicker() }
        
        btnSave.setOnClickListener {
            saveSettings()
        }
    }

    private fun setupSpinner() {
        val modes = CountdownMode.values()
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, modes.map { it.displayName })
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        spinnerMode.adapter = adapter
    }

    private fun loadCurrentValues() {
        etTitle.setText(prefs.getTitle())
        
        selectedDate = prefs.getTargetDate()
        updateDateTimeDisplay()
        
        val savedMode = prefs.getMode()
        spinnerMode.setSelection(CountdownMode.values().indexOf(savedMode))
    }

    private fun showDatePicker() {
        val datePicker = DatePickerDialog(
            this,
            { _, year, month, dayOfMonth ->
                selectedDate = selectedDate.withYear(year).withMonth(month + 1).withDayOfMonth(dayOfMonth)
                updateDateTimeDisplay()
            },
            selectedDate.year,
            selectedDate.monthValue - 1,
            selectedDate.dayOfMonth
        )
        datePicker.show()
    }

    private fun showTimePicker() {
        val timePicker = TimePickerDialog(
            this,
            { _, hourOfDay, minute ->
                selectedDate = selectedDate.withHour(hourOfDay).withMinute(minute)
                updateDateTimeDisplay()
            },
            selectedDate.hour,
            selectedDate.minute,
            true // 24 hour view
        )
        timePicker.show()
    }

    private fun updateDateTimeDisplay() {
        tvDate.text = selectedDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"))
        tvTime.text = selectedDate.format(DateTimeFormatter.ofPattern("HH:mm"))
    }

    private fun saveSettings() {
        val title = etTitle.text.toString()
        val modeIndex = spinnerMode.selectedItemPosition
        val mode = CountdownMode.values()[modeIndex]

        prefs.saveTitle(title)
        prefs.saveTargetDate(selectedDate)
        prefs.saveMode(mode)

        Toast.makeText(this, getString(R.string.saved_message), Toast.LENGTH_SHORT).show()
        
        promptSetWallpaper()
    }

    private fun promptSetWallpaper() {
        val intent = Intent(WallpaperManager.ACTION_CHANGE_LIVE_WALLPAPER)
        intent.putExtra(
            WallpaperManager.EXTRA_LIVE_WALLPAPER_COMPONENT,
            ComponentName(this, CountdownWallpaperService::class.java)
        )
        // Check if intent handles exist (some devices might behavior differently)
        try {
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(this, "Go to Settings -> Wallpaper to apply.", Toast.LENGTH_LONG).show()
        }
    }
}
