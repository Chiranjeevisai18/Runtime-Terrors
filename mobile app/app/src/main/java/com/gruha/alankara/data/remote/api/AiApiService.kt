package com.gruha.alankara.data.remote.api

import com.gruha.alankara.data.remote.dto.ColorExtractionResponse
import com.gruha.alankara.data.remote.dto.LayoutAnalysisRequest
import com.gruha.alankara.data.remote.dto.LayoutAnalysisResponse
import com.gruha.alankara.data.remote.dto.RoomAnalysisResponse
import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface AiApiService {
    @Multipart
    @POST("api/ai/analyze-room")
    suspend fun analyzeRoom(
        @Part image: MultipartBody.Part
    ): Response<RoomAnalysisResponse>

    @Multipart
    @POST("api/ai/extract-colors")
    suspend fun extractColors(
        @Part image: MultipartBody.Part
    ): Response<ColorExtractionResponse>

    @POST("api/ai/analyze-layout")
    suspend fun analyzeLayout(
        @Body request: LayoutAnalysisRequest
    ): Response<LayoutAnalysisResponse>
}
