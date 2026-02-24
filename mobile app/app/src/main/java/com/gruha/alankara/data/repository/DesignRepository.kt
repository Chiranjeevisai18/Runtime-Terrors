package com.gruha.alankara.data.repository

import com.gruha.alankara.data.remote.api.DesignApiService
import com.gruha.alankara.data.remote.dto.DesignResponse
import com.gruha.alankara.data.remote.dto.SaveDesignRequest
import com.gruha.alankara.data.local.dao.DesignDao
import com.gruha.alankara.data.local.entity.DesignEntity
import com.gruha.alankara.util.TokenManager
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DesignRepository @Inject constructor(
    private val apiService: DesignApiService,
    private val designDao: DesignDao,
    private val tokenManager: TokenManager
) {
    suspend fun saveDesign(request: SaveDesignRequest): Result<DesignResponse> {
        return try {
            val response = apiService.saveDesign(request)
            if (response.isSuccessful && response.body() != null) {
                val designDto = response.body()!!
                
                // Save to local cache
                val userId = tokenManager.getUserId() ?: ""
                designDao.insertDesign(
                    DesignEntity(
                        id = designDto.id.toLong(),
                        userId = userId,
                        name = designDto.name,
                        description = designDto.description ?: "",
                        anchorsJson = com.google.gson.Gson().toJson(designDto.objects),
                        updatedAt = System.currentTimeMillis()
                    )
                )
                
                Result.success(designDto)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to save design"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun getLocalDesigns(): Flow<List<DesignEntity>> {
        val userId = tokenManager.getUserId() ?: ""
        return designDao.getDesignsByUser(userId)
    }

    suspend fun getDesignById(id: Long): DesignEntity? {
        return designDao.getDesignById(id)
    }

    suspend fun refreshDesigns(): Result<Unit> {
        return try {
            val response = apiService.getDesigns()
            if (response.isSuccessful && response.body() != null) {
                val remoteDesigns = response.body()!!
                val userId = tokenManager.getUserId() ?: ""
                
                // Clear and update local cache
                designDao.deleteAllDesigns(userId)
                remoteDesigns.forEach { designDto ->
                    designDao.insertDesign(
                        DesignEntity(
                            id = designDto.id.toLong(),
                            userId = userId,
                            name = designDto.name,
                            description = designDto.description ?: "",
                            anchorsJson = com.google.gson.Gson().toJson(designDto.objects),
                            updatedAt = System.currentTimeMillis()
                        )
                    )
                }
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to refresh designs"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getDesigns(): Result<List<DesignResponse>> {
        return try {
            val response = apiService.getDesigns()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to fetch designs"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteDesign(id: Int): Result<Unit> {
        return try {
            val response = apiService.deleteDesign(id)
            if (response.isSuccessful) {
                // Remove from local cache
                designDao.deleteDesign(id.toLong())
                Result.success(Unit)
            } else {
                Result.failure(Exception(response.errorBody()?.string() ?: "Failed to delete design"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
