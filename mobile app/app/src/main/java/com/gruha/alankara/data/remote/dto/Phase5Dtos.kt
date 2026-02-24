package com.gruha.alankara.data.remote.dto

import com.google.gson.annotations.SerializedName

data class ProductSearchRequest(
    @SerializedName("query") val query: String
)

data class ProductDto(
    @SerializedName("id") val id: Int,
    @SerializedName("title") val title: String,
    @SerializedName("vendor") val vendor: String,
    @SerializedName("url") val url: String,
    @SerializedName("price") val price: String?,
    @SerializedName("rating") val rating: String?,
    @SerializedName("image_url") val imageUrl: String?
)

data class ProductSearchResponse(
    @SerializedName("message") val message: String,
    @SerializedName("query") val query: String,
    @SerializedName("results") val results: List<ProductDto>
)

data class BookingRequest(
    @SerializedName("product_url") val productUrl: String
)

data class BookingResumeRequest(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("answer") val answer: String
)

data class BookingResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String?,
    @SerializedName("order_id") val orderId: String?,
    @SerializedName("reason") val reason: String?,
    @SerializedName("redirect_url") val redirectUrl: String?,
    @SerializedName("question") val question: String?,
    @SerializedName("session_id") val sessionId: String?
)
