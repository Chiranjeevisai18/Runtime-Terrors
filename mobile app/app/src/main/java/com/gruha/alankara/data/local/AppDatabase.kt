package com.gruha.alankara.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.gruha.alankara.data.local.dao.DesignDao
import com.gruha.alankara.data.local.dao.UserDao
import com.gruha.alankara.data.local.entity.DesignEntity
import com.gruha.alankara.data.local.entity.UserEntity

@Database(
    entities = [UserEntity::class, DesignEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun designDao(): DesignDao
}
