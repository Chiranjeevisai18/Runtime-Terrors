# Add project specific ProGuard rules here.

# Keep Retrofit service interfaces
-keep,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}

# Keep Gson serialization models
-keepclassmembers class com.gruha.alankara.data.remote.dto.** {
    <fields>;
}

# Keep Room entities
-keep class com.gruha.alankara.data.local.entity.** { *; }

# SceneView / Filament
-keep class com.google.ar.** { *; }
-keep class io.github.sceneview.** { *; }
