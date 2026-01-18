package com.dashman.android.camera

import android.annotation.SuppressLint
import android.content.Context
import android.util.Log
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.video.*
import androidx.core.content.ContextCompat
import androidx.lifecycle.LifecycleOwner
import kotlinx.coroutines.*
import java.io.File
import java.text.SimpleDateFormat
import java.util.*
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraBufferManager(private val context: Context) {

    private var videoCapture: VideoCapture<Recorder>? = null
    private var activeRecording: Recording? = null
    private var cameraExecutor: ExecutorService = Executors.newSingleThreadExecutor()
    
    private val bufferFiles = ArrayDeque<File>()
    private var BUFFER_SIZE = 3 // Default 30s, updated from prefs
    private val SEGMENT_DURATION_MS = 10_000L

    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var segmentTimerJob: Job? = null
    private var onNextFinalize: (() -> Unit)? = null
    
    fun startCamera(lifecycleOwner: LifecycleOwner) {
        updateSettings()
        val cameraProviderFuture = ProcessCameraProvider.getInstance(context)
        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()
            
            // Preview Use Case (Optional, handled separately if UI needs it, 
            // but for Service-based background recording we focus on VideoCapture)
            // Ideally we'd separate Preview binding to Activity and Video to Service.
            // For now, we assume this is called by Service to bind VideoCapture.

            val recorder = Recorder.Builder()
                .setQualitySelector(QualitySelector.from(Quality.HD))
                .build()
                
            videoCapture = VideoCapture.withOutput(recorder)

            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA

            try {
                // Unbind only VideoCapture to avoid killing Preview if bound elsewhere?
                // CameraX requires unbinding to rebind.
                // For simplicity in this "Service-centric" mode:
                cameraProvider.unbindAll() 
                
                cameraProvider.bindToLifecycle(
                    lifecycleOwner,
                    cameraSelector,
                    videoCapture
                )
                
                startSegmentRecording()

            } catch (exc: Exception) {
                Log.e(TAG, "Use case binding failed", exc)
            }

        }, ContextCompat.getMainExecutor(context))
    }
    
    // Segment Loop
    private fun startSegmentRecording() {
        if (videoCapture == null) return

        val videoFile = createVideoConfig()
        
        val outputOptions = FileOutputOptions.Builder(videoFile).build()
        
        activeRecording = videoCapture!!.output
            .prepareRecording(context, outputOptions)
            .withAudioEnabled()
            .start(ContextCompat.getMainExecutor(context)) { recordEvent ->
                when(recordEvent) {
                    is VideoRecordEvent.Start -> {
                        Log.d(TAG, "Recording started: ${videoFile.name}")
                        scheduleNextSegment()
                    }
                    is VideoRecordEvent.Finalize -> {
                        if (!recordEvent.hasError()) {
                            Log.d(TAG, "Recording finished: ${videoFile.name}")
                            manageBuffer(videoFile)
                            onNextFinalize?.invoke()
                            onNextFinalize = null
                        } else {
                            activeRecording?.close()
                            activeRecording = null
                            Log.e(TAG, "Recording error: ${recordEvent.error}")
                        }
                    }
                }
            }
    }

    private fun scheduleNextSegment() {
        segmentTimerJob = scope.launch {
            delay(SEGMENT_DURATION_MS)
            // Stop current, which prompts Finalize, which we can then start next?
            // To minimize gap, we might want to start next immediately after stop.
            // But we need to call stop() on activeRecording.
            activeRecording?.stop()
            activeRecording = null
            
            // Start next immediately
            // Note: There is a small gap here. 
            // Real gapless requires low-level MediaCodec or vendor extensions.
            startSegmentRecording() 
        }
    }

    suspend fun flushCurrentSegment() = suspendCancellableCoroutine<Unit> { cont ->
        // 1. Cancel the automatic timer so we don't stop the NEXT one prematurely
        segmentTimerJob?.cancel()

        // 2. Setup the latch
        // We expect the currently running recording to finalize soon.
        onNextFinalize = {
            if (cont.isActive) cont.resume(Unit) { }
        }

        // 3. Stop (triggers Finalize)
        activeRecording?.stop()
        activeRecording = null

        // 4. Start next immediately (to minimize gap)
        startSegmentRecording()
    }

    private var isIncidentActive = false

    fun setIncidentCapture(active: Boolean) {
        synchronized(bufferFiles) {
            isIncidentActive = active
            if (!active) {
                // If turning off, enforce buffer size immediately
                while (bufferFiles.size > BUFFER_SIZE) {
                    val oldFile = bufferFiles.removeFirst()
                    if (oldFile.exists()) oldFile.delete()
                }
            }
        }
    }

    private fun manageBuffer(newFile: File) {
        synchronized(bufferFiles) {
            bufferFiles.addLast(newFile)
            
            if (!isIncidentActive) {
                while (bufferFiles.size > BUFFER_SIZE) {
                    val oldFile = bufferFiles.removeFirst()
                    if (oldFile.exists()) {
                        oldFile.delete()
                        Log.d(TAG, "Deleted old segment: ${oldFile.name}")
                    }
                }
            } else {
                Log.d(TAG, "Incident active: Keeping segment ${newFile.name}")
            }
        }
    }

    private fun createVideoConfig(): File {
        val timestamp = SimpleDateFormat("yyyyMMdd_HHmmss_SSS", Locale.US).format(System.currentTimeMillis())
        val dir = File(context.filesDir, "dashcam_buffer")
        if (!dir.exists()) dir.mkdirs()
        return File(dir, "VID_${timestamp}.mp4")
    }
    
    fun stopRecording() {
        activeRecording?.stop()
        activeRecording = null
        scope.cancel() // Stop the loop
        cameraExecutor.shutdown()
    }
    
    // Method to "Lock" the current files for an incident
    fun lockBufferForIncident(): List<File> {
        synchronized(bufferFiles) {
            // Return copy of current buffer
            return ArrayList(bufferFiles)
        }
    }

    private fun updateSettings() {
        val prefs = context.getSharedPreferences("dashman_prefs", Context.MODE_PRIVATE)
        val bufferSeconds = prefs.getInt("buffer_seconds", 30)
        // Each segment is 10s
        BUFFER_SIZE = (bufferSeconds / 10).coerceAtLeast(1)
        Log.i(TAG, "Buffer size set to $BUFFER_SIZE segments ($bufferSeconds seconds)")
    }

    companion object {
        private const val TAG = "CameraBufferManager"
    }
}
