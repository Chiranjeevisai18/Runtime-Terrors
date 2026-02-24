package com.gruha.alankara.data.remote.api

import com.gruha.alankara.data.remote.dto.DesignResponse
import com.gruha.alankara.data.remote.dto.SaveDesignRequest
import retrofit2.Response
import retrofit2.http.*

interface DesignApiService {
    @POST("api/designs")
    suspend fun saveDesign(@Body request: SaveDesignRequest): Response<DesignResponse>

    @GET("api/designs")
    suspend fun getDesigns(): Response<List<DesignResponse>>

    @GET("api/designs/{id}")
    suspend fun getDesign(@Path("id") id: Int): Response<DesignResponse>

    @DELETE("api/designs/{id}")
    suspend fun deleteDesign(@Path("id") id: Int): Response<Unit>
}
