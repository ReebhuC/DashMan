package com.dashman.android

import android.content.Context
import android.os.Bundle
import android.widget.Button
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class SettingsActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        val prefs = getSharedPreferences("dashman_prefs", Context.MODE_PRIVATE)

        val seekSensitivity = findViewById<SeekBar>(R.id.seekSensitivity)
        val sensitivityValue = findViewById<TextView>(R.id.sensitivityValue)
        val radioGroup = findViewById<RadioGroup>(R.id.radioGroupBuffer)
        val switchOverlay = findViewById<Switch>(R.id.switchOverlay)
        val btnSave = findViewById<Button>(R.id.btnSave)

        // Load saved values
        val savedThreshold = prefs.getFloat("sensitivity_threshold", 15.0f)
        val savedBuffer = prefs.getInt("buffer_seconds", 30)
        val savedOverlay = prefs.getBoolean("video_overlay_srt", true)

        // Set UI state
        seekSensitivity.progress = (savedThreshold * 10).toInt()
        sensitivityValue.text = "${String.format("%.1f", savedThreshold)} G"

        when (savedBuffer) {
            30 -> radioGroup.check(R.id.rb30s)
            60 -> radioGroup.check(R.id.rb60s)
            120 -> radioGroup.check(R.id.rb120s)
            else -> radioGroup.check(R.id.rb30s)
        }
        
        switchOverlay.isChecked = savedOverlay

        // Listeners
        seekSensitivity.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                val gVal = progress / 10.0f
                sensitivityValue.text = "${String.format("%.1f", gVal)} G"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        btnSave.setOnClickListener {
            val editor = prefs.edit()
            
            // Save Sensitivity
            editor.putFloat("sensitivity_threshold", seekSensitivity.progress / 10.0f)

            // Save Buffer
            val selectedId = radioGroup.checkedRadioButtonId
            val bufferSeconds = when (selectedId) {
                R.id.rb30s -> 30
                R.id.rb60s -> 60
                R.id.rb120s -> 120
                else -> 30
            }
            editor.putInt("buffer_seconds", bufferSeconds)
            
            // Save Overlay
            editor.putBoolean("video_overlay_srt", switchOverlay.isChecked)

            editor.apply()
            
            Toast.makeText(this, "Settings Saved", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
}
