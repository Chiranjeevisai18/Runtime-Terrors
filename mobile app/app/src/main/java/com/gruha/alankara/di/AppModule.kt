package com.gruha.alankara.di

import android.content.Context
import androidx.room.Room
import com.gruha.alankara.data.local.AppDatabase
import com.gruha.alankara.data.local.dao.DesignDao
import com.gruha.alankara.data.local.dao.UserDao
import com.gruha.alankara.data.remote.AuthInterceptor
import com.gruha.alankara.data.remote.api.AiApiService
import com.gruha.alankara.data.remote.api.AuthApiService
import com.gruha.alankara.data.remote.api.AssistantApiService
import com.gruha.alankara.data.remote.api.DesignApiService
import com.gruha.alankara.data.remote.api.ProductApiService
import com.gruha.alankara.util.Constants
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    // ===== Networking =====

    @Provides
    @Singleton
    fun provideOkHttpClient(authInterceptor: AuthInterceptor): OkHttpClient {
        val loggingInterceptor = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val bypassInterceptor = okhttp3.Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("Bypass-Tunnel-Reminder", "true")
                .addHeader("ngrok-skip-browser-warning", "true")
                .build()
            chain.proceed(request)
        }

        return OkHttpClient.Builder()
            .addInterceptor(bypassInterceptor)
            .addInterceptor(authInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(60, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(Constants.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideAuthApiService(retrofit: Retrofit): AuthApiService {
        return retrofit.create(AuthApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideAiApiService(retrofit: Retrofit): AiApiService {
        return retrofit.create(AiApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideDesignApiService(retrofit: Retrofit): DesignApiService {
        return retrofit.create(DesignApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideAssistantApiService(retrofit: Retrofit): AssistantApiService {
        return retrofit.create(AssistantApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideProductApiService(retrofit: Retrofit): ProductApiService {
        return retrofit.create(ProductApiService::class.java)
    }

    // ===== Database =====

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            Constants.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }

    @Provides
    fun provideDesignDao(database: AppDatabase): DesignDao {
        return database.designDao()
    }
}
