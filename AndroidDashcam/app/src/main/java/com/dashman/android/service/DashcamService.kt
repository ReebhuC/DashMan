package com.dashman.android.service

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.lifecycle.LifecycleService
import com.dashman.android.MainActivity
import com.dashman.android.R
import com.dashman.android.camera.CameraBufferManager
import com.dashman.android.sensor.SensorManagerModule
import com.dashman.android.location.GPSManager
import com.dashman.android.logic.IncidentStateMachine


class DashcamService : LifecycleService() {

    private lateinit var cameraBufferManager: CameraBufferManager
    private lateinit var sensorManager: SensorManagerModule
    private lateinit var gpsManager: GPSManager
    private lateinit var incidentStateMachine: IncidentStateMachine

    override fun onCreate() {
        super.onCreate()
        cameraBufferManager = CameraBufferManager(this)
        sensorManager = SensorManagerModule(this)
        gpsManager = GPSManager(this)
        
        incidentStateMachine = IncidentStateMachine(
            this,
            cameraBufferManager,
            sensorManager,
            gpsManager
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        super.onStartCommand(intent, flags, startId)
        
        when(intent?.action) {
            ACTION_START -> startForegroundService()
            ACTION_STOP -> stopForegroundService()
        }
        
        return Service.START_STICKY
    }
    
    private fun startForegroundService() {
        createNotificationChannel()
        val notification = createNotification()
        startForeground(NOTIFICATION_ID, notification)
        
        if (checkPermissions()) {
            cameraBufferManager.startCamera(this)
            incidentStateMachine.start()
            Log.d(TAG, "Dashcam Service Started & Listening")
        } else {
            Log.e(TAG, "Permissions missing for service")
            stopSelf()
        }
    }
    
    private fun stopForegroundService() {
        incidentStateMachine.stop()
        cameraBufferManager.stopRecording()
        stopForeground(true)
        stopSelf()
    }
    
    private fun createNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE)

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("DashMan Active")
            .setContentText("Recording & Monitoring...")
            .setSmallIcon(android.R.drawable.ic_menu_camera)
            .setContentIntent(pendingIntent)
            .build()

    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID, "DashMan Service Channel",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(serviceChannel)
        }
    }
    
    private fun checkPermissions(): Boolean {
        return ActivityCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED &&
               ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
    }

    companion object {
        const val TAG = "DashcamService"
        const val ACTION_START = "ACTION_START"
        const val ACTION_STOP = "ACTION_STOP"
        const val CHANNEL_ID = "DashcamChannel"
        const val NOTIFICATION_ID = 1
    }
}
