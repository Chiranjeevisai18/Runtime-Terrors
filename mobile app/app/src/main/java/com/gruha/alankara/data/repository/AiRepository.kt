package com.gruha.alankara.data.repository

import com.gruha.alankara.data.remote.api.AiApiService
import com.gruha.alankara.data.remote.dto.ColorExtractionResponse
import com.gruha.alankara.data.remote.dto.LayoutAnalysisRequest
import com.gruha.alankara.data.remote.dto.LayoutAnalysisResponse
import com.gruha.alankara.data.remote.dto.RoomAnalysisResponse
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AiRepository @Inject constructor(
    private val apiService: AiApiService
) {
    suspend fun analyzeRoom(imageBytes: ByteArray): Result<RoomAnalysisResponse> {
        val requestFile = imageBytes.toRequestBody("image/jpeg".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("image", "room.jpg", requestFile)

        return try {
            val response = apiService.analyzeRoom(body)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Analysis failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun extractColors(imageBytes: ByteArray): Result<ColorExtractionResponse> {
        val requestFile = imageBytes.toRequestBody("image/jpeg".toMediaTypeOrNull())
        val body = MultipartBody.Part.createFormData("image", "theme.jpg", requestFile)

        return try {
            val response = apiService.extractColors(body)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Color extraction failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun analyzeLayout(request: LayoutAnalysisRequest): Result<LayoutAnalysisResponse> {
        return try {
            val response = apiService.analyzeLayout(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Layout analysis failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
