package com.gruha.alankara.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val GruhaDarkColorScheme = darkColorScheme(
    primary = VioletPrimary,
    onPrimary = TextPrimary,
    primaryContainer = VioletDark,
    onPrimaryContainer = VioletLight,
    secondary = CyanSecondary,
    onSecondary = DeepSlate,
    secondaryContainer = CyanDark,
    onSecondaryContainer = CyanLight,
    tertiary = CyanLight,
    onTertiary = DeepSlate,
    background = DeepSlate,
    onBackground = TextPrimary,
    surface = SurfaceDark,
    onSurface = TextPrimary,
    surfaceVariant = CardDark,
    onSurfaceVariant = TextSecondary,
    error = ErrorRed,
    onError = TextPrimary,
    errorContainer = ErrorRedDark,
    onErrorContainer = TextPrimary,
    outline = TextTertiary,
    outlineVariant = TextDisabled,
    scrim = Scrim,
    inverseSurface = TextPrimary,
    inverseOnSurface = DeepSlate,
    inversePrimary = VioletDark,
    surfaceTint = VioletPrimary
)

@Composable
fun GruhaAlankaraTheme(
    content: @Composable () -> Unit
) {
    val colorScheme = GruhaDarkColorScheme
    val view = LocalView.current

    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            window.navigationBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = false
                isAppearanceLightNavigationBars = false
            }
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = GruhaTypography,
        shapes = GruhaShapes,
        content = content
    )
}
