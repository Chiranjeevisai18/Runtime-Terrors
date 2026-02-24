package com.gruha.alankara.data.remote.api

import com.gruha.alankara.data.remote.dto.*
import retrofit2.http.Body
import retrofit2.http.POST

interface ProductApiService {
    @POST("products/search")
    suspend fun searchProducts(
        @Body request: ProductSearchRequest
    ): ProductSearchResponse

    @POST("products/book")
    suspend fun autoBook(
        @Body request: BookingRequest
    ): BookingResponse

    @POST("products/book/resume")
    suspend fun resumeBooking(
        @Body request: BookingResumeRequest
    ): BookingResponse
}
