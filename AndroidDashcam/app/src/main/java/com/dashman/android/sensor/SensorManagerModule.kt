package com.dashman.android.sensor

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import java.util.concurrent.ConcurrentLinkedDeque

data class SensorData(
    val timestamp: Long,
    val type: Int, // Sensor.TYPE_ACCELEROMETER or TYPE_GYROSCOPE
    val x: Float,
    val y: Float,
    val z: Float
)

class SensorManagerModule(context: Context) : SensorEventListener {

    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
    private val gyroscope = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE)
    
    // Circular buffer for sensor data
    private val dataBuffer = ConcurrentLinkedDeque<SensorData>()
    private val BUFFER_DURATION_MS = 60_000L // 60 seconds history
    
    var onSensorDataListener: ((SensorData) -> Unit)? = null

    fun startSensors() {
        accelerometer?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
        gyroscope?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME)
        }
    }

    fun stopSensors() {
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        event?.let {
            val data = SensorData(
                timestamp = System.currentTimeMillis(),
                type = it.sensor.type,
                x = it.values[0],
                y = it.values[1],
                z = it.values[2]
            )
            
            // Add to buffer
            dataBuffer.add(data)
            
            // Notify listener (IncidentDetector)
            onSensorDataListener?.invoke(data)
            
            // Cleanup old data periodically or on every add? 
            // cleaning every add might be expensive if high freq. 
            // For optimized approach, clean up less frequently or use a fixed size ring buffer.
            // For now, simple time check:
            cleanBuffer()
        }
    }
    
    private fun cleanBuffer() {
        val now = System.currentTimeMillis()
        while (!dataBuffer.isEmpty() && (now - dataBuffer.peekFirst()!!.timestamp > BUFFER_DURATION_MS)) {
            dataBuffer.pollFirst()
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // No-op
    }
    
    fun getBufferedData(): List<SensorData> {
        return ArrayList(dataBuffer)
    }
}
