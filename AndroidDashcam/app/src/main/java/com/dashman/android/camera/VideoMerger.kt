package com.dashman.android.camera

import android.util.Log
import com.googlecode.mp4parser.authoring.Movie
import com.googlecode.mp4parser.authoring.Track
import com.googlecode.mp4parser.authoring.builder.DefaultMp4Builder
import com.googlecode.mp4parser.authoring.container.mp4.MovieCreator
import com.googlecode.mp4parser.authoring.tracks.AppendTrack
import java.io.File
import java.io.RandomAccessFile
import java.util.LinkedList

object VideoMerger {
    private const val TAG = "VideoMerger"

    fun mergeVideos(files: List<File>, outputFile: File): Boolean {
        if (files.isEmpty()) return false
        
        try {
            val movies = LinkedList<Movie>()
            for (file in files) {
                if (file.exists()) {
                    movies.add(MovieCreator.build(file.absolutePath))
                }
            }
            
            val videoTracks = LinkedList<Track>()
            val audioTracks = LinkedList<Track>()
            
            for (movie in movies) {
                for (track in movie.tracks) {
                    if (track.handler == "vide") {
                        videoTracks.add(track)
                    }
                    if (track.handler == "soun") {
                        audioTracks.add(track)
                    }
                }
            }
            
            val resultMovie = Movie()
            
            if (videoTracks.isNotEmpty()) {
                resultMovie.addTrack(AppendTrack(*videoTracks.toTypedArray()))
            }
            if (audioTracks.isNotEmpty()) {
                resultMovie.addTrack(AppendTrack(*audioTracks.toTypedArray()))
            }
            
            val container = DefaultMp4Builder().build(resultMovie)
            
            val fc = RandomAccessFile(outputFile, "rw").channel
            container.writeContainer(fc)
            fc.close()
            
            return true
            
        } catch (e: Exception) {
            Log.e(TAG, "Error merging videos", e)
            return false
        }
    }

    fun getDuration(file: File): Long {
         try {
             val movie = MovieCreator.build(file.absolutePath)
             val durationProp = movie.tracks.firstOrNull()?.duration ?: 0
             val timescal = movie.tracks.firstOrNull()?.trackMetaData?.timescale ?: 1
             return (durationProp * 1000) / timescal
         } catch (e: Exception) {
             return 0L
         }
    }
}
