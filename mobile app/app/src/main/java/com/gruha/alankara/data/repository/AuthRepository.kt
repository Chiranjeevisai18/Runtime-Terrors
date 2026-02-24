package com.gruha.alankara.data.repository

import com.gruha.alankara.data.local.dao.UserDao
import com.gruha.alankara.data.local.entity.UserEntity
import com.gruha.alankara.data.remote.api.AuthApiService
import com.gruha.alankara.data.remote.dto.LoginRequest
import com.gruha.alankara.data.remote.dto.RegisterRequest
import com.gruha.alankara.domain.model.User
import com.gruha.alankara.util.TokenManager
import javax.inject.Inject
import javax.inject.Singleton

sealed class AuthResult {
    data class Success(val user: User) : AuthResult()
    data class Error(val message: String) : AuthResult()
}

@Singleton
class AuthRepository @Inject constructor(
    private val authApiService: AuthApiService,
    private val tokenManager: TokenManager,
    private val userDao: UserDao
) {

    suspend fun login(email: String, password: String): AuthResult {
        return try {
            val response = authApiService.login(LoginRequest(email, password))
            if (response.isSuccessful) {
                val body = response.body()!!
                tokenManager.saveToken(body.token)
                tokenManager.saveUserInfo(body.user.id, body.user.name, body.user.email)

                // Cache user locally
                userDao.insertUser(
                    UserEntity(
                        id = body.user.id,
                        name = body.user.name,
                        email = body.user.email
                    )
                )

                AuthResult.Success(
                    User(id = body.user.id, name = body.user.name, email = body.user.email)
                )
            } else {
                val errorMsg = response.errorBody()?.string() ?: "Login failed"
                AuthResult.Error(errorMsg)
            }
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Network error occurred")
        }
    }

    suspend fun register(name: String, email: String, password: String): AuthResult {
        return try {
            val response = authApiService.register(RegisterRequest(name, email, password))
            if (response.isSuccessful) {
                val body = response.body()!!
                if (body.token != null && body.user != null) {
                    tokenManager.saveToken(body.token)
                    tokenManager.saveUserInfo(body.user.id, body.user.name, body.user.email)

                    userDao.insertUser(
                        UserEntity(
                            id = body.user.id,
                            name = body.user.name,
                            email = body.user.email
                        )
                    )

                    AuthResult.Success(
                        User(id = body.user.id, name = body.user.name, email = body.user.email)
                    )
                } else {
                    AuthResult.Success(User(id = "", name = name, email = email))
                }
            } else {
                val errorMsg = response.errorBody()?.string() ?: "Registration failed"
                AuthResult.Error(errorMsg)
            }
        } catch (e: Exception) {
            AuthResult.Error(e.message ?: "Network error occurred")
        }
    }

    fun logout() {
        tokenManager.clearAll()
    }

    fun isLoggedIn(): Boolean = tokenManager.isLoggedIn()

    fun getCurrentUserName(): String? = tokenManager.getUserName()
    fun getCurrentUserEmail(): String? = tokenManager.getUserEmail()
}
