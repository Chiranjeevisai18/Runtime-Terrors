package com.gruha.alankara.data.repository

import com.gruha.alankara.data.remote.api.AssistantApiService
import com.gruha.alankara.data.remote.dto.AssistantChatRequest
import com.gruha.alankara.data.remote.dto.AssistantChatResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AssistantRepository @Inject constructor(
    private val apiService: AssistantApiService
) {
    suspend fun chat(request: AssistantChatRequest): Result<AssistantChatResponse> {
        return try {
            val response = apiService.chat(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception("Chat failed: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
