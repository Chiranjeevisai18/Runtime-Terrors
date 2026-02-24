package com.gruha.alankara.data.remote.dto

import com.google.gson.annotations.SerializedName

data class RegisterResponse(
    @SerializedName("message")
    val message: String,
    @SerializedName("token")
    val token: String?,
    @SerializedName("user")
    val user: UserDto?
)
