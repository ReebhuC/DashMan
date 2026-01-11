package com.dashman.android.upload

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import com.dashman.android.upload.RetrofitClient

class UploadWorker(context: Context, params: WorkerParameters) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val incidentPath = inputData.getString("incident_path") ?: return Result.failure()
        val incidentDir = File(incidentPath)
        
        if (!incidentDir.exists()) return Result.failure()
        
        val videoFile = File(incidentDir, "incident_clip.mp4")
        val sensorFile = File(incidentDir, "sensor_log.json")
        val gpsFile = File(incidentDir, "gps_log.json")
        
        if (!videoFile.exists()) return Result.failure()
        
        try {
            val api = RetrofitClient.api
            
            val videoPart = MultipartBody.Part.createFormData("video_file", videoFile.name, 
                videoFile.asRequestBody("video/mp4".toMediaTypeOrNull()))
            
            val sensorPart = MultipartBody.Part.createFormData("sensor_log", sensorFile.name, 
                sensorFile.asRequestBody("application/json".toMediaTypeOrNull()))
                
            val gpsPart = MultipartBody.Part.createFormData("gps_log", gpsFile.name, 
                gpsFile.asRequestBody("application/json".toMediaTypeOrNull()))
                
            val response = api.uploadIncident(videoPart, sensorPart, gpsPart)
            
            if (response.isSuccessful) {
                // Cleanup
                incidentDir.deleteRecursively()
                return Result.success()
            } else {
                return Result.retry()
            }
            
        } catch (e: Exception) {
            e.printStackTrace()
            return Result.retry()
        }
    }
}
