package com.dashman.android.location

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.os.Looper
import android.util.Log
import com.google.android.gms.location.*
import java.util.concurrent.ConcurrentLinkedDeque

data class GPSData(
    val timestamp: Long,
    val latitude: Double,
    val longitude: Double,
    val speed: Float,
    val accuracy: Float
)

class GPSManager(private val context: Context) {

    private val fusedLocationClient: FusedLocationProviderClient = LocationServices.getFusedLocationProviderClient(context)
    private val locationCallback: LocationCallback
    
    private val dataBuffer = ConcurrentLinkedDeque<GPSData>()
    private val BUFFER_DURATION_MS = 60_000L

    init {
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(locationResult: LocationResult) {
                locationResult.lastLocation?.let { location ->
                    handleLocation(location)
                }
            }
        }
    }

    @SuppressLint("MissingPermission") // Permissions checked by caller
    fun startLocationUpdates() {
        val locationRequest = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 1000)
            .setMinUpdateIntervalMillis(1000)
            .build()

        fusedLocationClient.requestLocationUpdates(locationRequest, locationCallback, Looper.getMainLooper())
    }

    fun stopLocationUpdates() {
        fusedLocationClient.removeLocationUpdates(locationCallback)
    }

    private fun handleLocation(location: Location) {
        val data = GPSData(
            timestamp = location.time,
            latitude = location.latitude,
            longitude = location.longitude,
            speed = location.speed,
            accuracy = location.accuracy
        )
        dataBuffer.add(data)
        cleanBuffer()
    }

    private fun cleanBuffer() {
        val now = System.currentTimeMillis()
        while (!dataBuffer.isEmpty() && (now - dataBuffer.peekFirst()!!.timestamp > BUFFER_DURATION_MS)) {
            dataBuffer.pollFirst()
        }
    }
    
    fun getBufferedData(): List<GPSData> {
        return ArrayList(dataBuffer)
    }
}
