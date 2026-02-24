package com.gruha.alankara.util

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext context: Context
) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        Constants.PREFS_NAME,
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        prefs.edit().putString(Constants.KEY_AUTH_TOKEN, token).apply()
    }

    fun getToken(): String? {
        return prefs.getString(Constants.KEY_AUTH_TOKEN, null)
    }

    fun clearToken() {
        prefs.edit().remove(Constants.KEY_AUTH_TOKEN).apply()
    }

    fun saveUserInfo(userId: String, name: String, email: String) {
        prefs.edit().apply {
            putString(Constants.KEY_USER_ID, userId)
            putString(Constants.KEY_USER_NAME, name)
            putString(Constants.KEY_USER_EMAIL, email)
            apply()
        }
    }

    fun getUserName(): String? = prefs.getString(Constants.KEY_USER_NAME, null)
    fun getUserEmail(): String? = prefs.getString(Constants.KEY_USER_EMAIL, null)
    fun getUserId(): String? = prefs.getString(Constants.KEY_USER_ID, null)

    fun isLoggedIn(): Boolean = getToken() != null

    fun clearAll() {
        prefs.edit().clear().apply()
    }
}
