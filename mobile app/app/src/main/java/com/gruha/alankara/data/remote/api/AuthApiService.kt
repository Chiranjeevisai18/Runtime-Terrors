package com.gruha.alankara.data.remote.api

import com.gruha.alankara.data.remote.dto.LoginRequest
import com.gruha.alankara.data.remote.dto.LoginResponse
import com.gruha.alankara.data.remote.dto.RegisterRequest
import com.gruha.alankara.data.remote.dto.RegisterResponse
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApiService {

    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("api/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<RegisterResponse>
}
