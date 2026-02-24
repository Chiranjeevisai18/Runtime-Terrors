package com.gruha.alankara.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.gruha.alankara.data.local.entity.DesignEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface DesignDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertDesign(design: DesignEntity): Long

    @Query("SELECT * FROM designs WHERE userId = :userId ORDER BY updatedAt DESC")
    fun getDesignsByUser(userId: String): Flow<List<DesignEntity>>

    @Query("SELECT * FROM designs WHERE id = :designId LIMIT 1")
    suspend fun getDesignById(designId: Long): DesignEntity?

    @Query("DELETE FROM designs WHERE id = :designId")
    suspend fun deleteDesign(designId: Long)

    @Query("DELETE FROM designs WHERE userId = :userId")
    suspend fun deleteAllDesigns(userId: String)
}
