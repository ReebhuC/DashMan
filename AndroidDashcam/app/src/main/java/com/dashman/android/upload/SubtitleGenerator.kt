package com.dashman.android.upload

import android.location.Location
import com.dashman.android.location.GPSData
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.TimeUnit

object SubtitleGenerator {

    /**
     * Generates an SRT subtitle file from GPS data.
     * @param videoStartTime: The absolute start time of the video in epoch ms.
     * @param videoDurationMs: Total duration of the merged video in ms.
     * @param gpsData: List of GPS points.
     * @param outputFile: The target .srt file.
     */
    fun generateSrt(
        videoStartTime: Long,
        videoDurationMs: Long,
        gpsData: List<GPSData>,
        outputFile: File
    ) {
        val sb = StringBuilder()
        var index = 1
        
        // We generate a subtitle every 1 second
        for (offset in 0 until videoDurationMs step 1000) {
            val currentTime = videoStartTime + offset
            val nextTime = currentTime + 1000
            
            // Find finding closest GPS point
            val point = findClosestPoint(gpsData, currentTime)
            
            if (point != null) {
                val startTimeStr = formatSrtTime(offset)
                val endTimeStr = formatSrtTime(offset + 1000)
                
                sb.append("$index\n")
                sb.append("$startTimeStr --> $endTimeStr\n")
                
                // Content: Date Time | Speed | Lat, Lon
                val dateStr = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(Date(currentTime))
                val speedKmh = (point.speed * 3.6).toInt()
                sb.append("$dateStr | $speedKmh km/h | ${point.latitude}, ${point.longitude}\n\n")
                
                index++
            }
        }
        
        outputFile.writeText(sb.toString())
    }
    
    private fun findClosestPoint(data: List<GPSData>, timeMs: Long): GPSData? {
        if (data.isEmpty()) return null
        // Simple search (can be optimized but list is small < 500 items usually)
        return data.minByOrNull { kotlin.math.abs(it.timestamp - timeMs) }
    }
    
    private fun formatSrtTime(millis: Long): String {
        val hours = TimeUnit.MILLISECONDS.toHours(millis)
        val minutes = TimeUnit.MILLISECONDS.toMinutes(millis) % 60
        val seconds = TimeUnit.MILLISECONDS.toSeconds(millis) % 60
        val ms = millis % 1000
        return String.format("%02d:%02d:%02d,%03d", hours, minutes, seconds, ms)
    }
}
