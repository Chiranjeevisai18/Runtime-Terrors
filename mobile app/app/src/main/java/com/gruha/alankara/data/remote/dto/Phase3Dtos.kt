package com.gruha.alankara.data.remote.dto

import com.google.gson.annotations.SerializedName

data class ColorExtractionResponse(
    @SerializedName("dominant_color") val dominantColor: String,
    @SerializedName("palette") val palette: List<String>,
    @SerializedName("recommended_style") val recommendedStyle: String
)

data class LayoutAnalysisRequest(
    @SerializedName("objects") val objects: List<DesignObjectDto>
)

data class LayoutAnalysisResponse(
    @SerializedName("clutter_score") val clutterScore: Double,
    @SerializedName("suggestions") val suggestions: List<String>
)

data class AssistantChatRequest(
    @SerializedName("context_id") val contextId: String? = null,
    @SerializedName("user_message") val userMessage: String,
    @SerializedName("room_type") val roomType: String?,
    @SerializedName("detected_objects") val detectedObjects: List<String>,
    @SerializedName("current_furniture") val currentFurniture: List<String>,
    @SerializedName("style_theme") val styleTheme: String
)

data class AssistantChatResponse(
    @SerializedName("text") val text: String,
    @SerializedName("suggested_action") val suggestedAction: String?
)
