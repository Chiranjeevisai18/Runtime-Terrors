package com.gruha.alankara.ui.auth

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gruha.alankara.ui.components.GlassCard
import com.gruha.alankara.ui.components.GruhaButton
import com.gruha.alankara.ui.components.GruhaTextField
import com.gruha.alankara.ui.theme.*

@Composable
fun LoginScreen(
    uiState: AuthUiState,
    onEmailChanged: (String) -> Unit,
    onPasswordChanged: (String) -> Unit,
    onLoginClick: () -> Unit,
    onNavigateToRegister: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(DeepSlate, SurfaceDark, DeepSlate)
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Spacer(modifier = Modifier.height(80.dp))

            // App branding
            Text(
                text = "✦",
                fontSize = 48.sp,
                color = VioletPrimary
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Gruha Alankara",
                style = MaterialTheme.typography.displayMedium,
                color = TextPrimary,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "AR Interior Design",
                style = MaterialTheme.typography.titleMedium,
                color = CyanSecondary,
                letterSpacing = 3.sp
            )

            Spacer(modifier = Modifier.height(48.dp))

            // Login card
            GlassCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Welcome Back",
                    style = MaterialTheme.typography.headlineMedium,
                    color = TextPrimary
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Sign in to continue",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )

                Spacer(modifier = Modifier.height(24.dp))

                GruhaTextField(
                    value = uiState.email,
                    onValueChange = onEmailChanged,
                    label = "Email",
                    leadingIcon = Icons.Outlined.Email,
                    keyboardType = KeyboardType.Email,
                    isError = uiState.emailError != null,
                    errorMessage = uiState.emailError,
                    imeAction = ImeAction.Next
                )

                Spacer(modifier = Modifier.height(16.dp))

                GruhaTextField(
                    value = uiState.password,
                    onValueChange = onPasswordChanged,
                    label = "Password",
                    leadingIcon = Icons.Outlined.Lock,
                    isPassword = true,
                    isError = uiState.passwordError != null,
                    errorMessage = uiState.passwordError,
                    imeAction = ImeAction.Done,
                    onImeAction = onLoginClick
                )

                // Error message
                AnimatedVisibility(
                    visible = uiState.errorMessage != null,
                    enter = fadeIn() + expandVertically(),
                    exit = fadeOut() + shrinkVertically()
                ) {
                    Text(
                        text = uiState.errorMessage ?: "",
                        color = ErrorRed,
                        style = MaterialTheme.typography.bodySmall,
                        textAlign = TextAlign.Center,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 12.dp)
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                GruhaButton(
                    text = "Sign In",
                    onClick = onLoginClick,
                    isLoading = uiState.isLoading
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Register link
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Don't have an account? ",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
                Text(
                    text = "Sign Up",
                    style = MaterialTheme.typography.bodyMedium,
                    color = CyanSecondary,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.clickable(onClick = onNavigateToRegister)
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
