package com.gruha.alankara.data.remote.api

import com.gruha.alankara.data.remote.dto.AssistantChatRequest
import com.gruha.alankara.data.remote.dto.AssistantChatResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AssistantApiService {
    @POST("api/assistant/chat")
    suspend fun chat(
        @Body request: AssistantChatRequest
    ): Response<AssistantChatResponse>
}
