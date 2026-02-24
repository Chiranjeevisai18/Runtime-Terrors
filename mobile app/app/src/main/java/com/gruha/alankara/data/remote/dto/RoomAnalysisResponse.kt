package com.gruha.alankara.data.remote.dto

import com.google.gson.annotations.SerializedName

data class RoomAnalysisResponse(
    @SerializedName("context_id") val contextId: String?,
    @SerializedName("room_type") val roomType: String,
    @SerializedName("description") val description: String,
    @SerializedName("detected_objects") val detectedObjects: List<String>,
    @SerializedName("recommended_items") val recommendedItems: List<RecommendedFurnitureDto>
)

data class RecommendedFurnitureDto(
    @SerializedName("model_id") val modelId: String,
    @SerializedName("name") val name: String
)
