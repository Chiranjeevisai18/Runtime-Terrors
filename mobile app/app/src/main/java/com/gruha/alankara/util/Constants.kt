package com.gruha.alankara.util

object Constants {
    // Backend base URL - use your PC's Wi-Fi IP for physical device testing
    // Local IP: http://10.100.10.116:5000/
    // Tunnel: https://gruha-buddy-ai.loca.lt/
    const val BASE_URL = "http://10.100.10.116:5000/"

    // API endpoints
    const val LOGIN_ENDPOINT = "api/auth/login"
    const val REGISTER_ENDPOINT = "api/auth/register"

    // SharedPreferences keys
    const val PREFS_NAME = "gruha_alankara_prefs"
    const val KEY_AUTH_TOKEN = "auth_token"
    const val KEY_USER_ID = "user_id"
    const val KEY_USER_NAME = "user_name"
    const val KEY_USER_EMAIL = "user_email"

    // AR constants
    const val MAX_OBJECTS_PER_SESSION = 20
    const val DEFAULT_MODEL_SCALE = 0.5f
    const val MIN_MODEL_SCALE = 0.1f
    const val MAX_MODEL_SCALE = 3.0f

    // Database
    const val DATABASE_NAME = "gruha_alankara_db"
    const val DATABASE_VERSION = 1
}
