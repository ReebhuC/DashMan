package com.dashman.android.upload

import okhttp3.MultipartBody
import okhttp3.ResponseBody
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface DashcamAPI {
    @Multipart
    @POST("incident/upload")
    suspend fun uploadIncident(
        @Part video: MultipartBody.Part,
        @Part sensorLog: MultipartBody.Part,
        @Part gpsLog: MultipartBody.Part
    ): Response<ResponseBody>
}

object RetrofitClient {
    private const val BASE_URL = "http://172.20.223.186:5000/" // Local IP

    val api: DashcamAPI by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(DashcamAPI::class.java)
    }
}
