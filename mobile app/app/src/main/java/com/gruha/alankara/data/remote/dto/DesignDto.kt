package com.gruha.alankara.data.remote.dto

import com.google.gson.annotations.SerializedName

data class SaveDesignRequest(
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String = "",
    @SerializedName("objects") val objects: List<DesignObjectDto>
)

data class DesignObjectDto(
    @SerializedName("model_id") val modelId: String,
    @SerializedName("position") val position: Vector3Dto,
    @SerializedName("rotation") val rotation: Float,
    @SerializedName("scale") val scale: Float
)

data class Vector3Dto(
    @SerializedName("x") val x: Float,
    @SerializedName("y") val y: Float,
    @SerializedName("z") val z: Float
)

data class DesignResponse(
    @SerializedName("id") val id: Int,
    @SerializedName("user_id") val userId: String,
    @SerializedName("name") val name: String,
    @SerializedName("description") val description: String,
    @SerializedName("objects") val objects: List<DesignObjectDto>,
    @SerializedName("created_at") val createdAt: String?
)
