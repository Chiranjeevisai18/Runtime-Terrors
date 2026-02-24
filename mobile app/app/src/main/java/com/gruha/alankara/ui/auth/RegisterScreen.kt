package com.gruha.alankara.ui.auth

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.material.icons.outlined.Email
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Person
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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RegisterScreen(
    uiState: AuthUiState,
    onNameChanged: (String) -> Unit,
    onEmailChanged: (String) -> Unit,
    onPasswordChanged: (String) -> Unit,
    onConfirmPasswordChanged: (String) -> Unit,
    onRegisterClick: () -> Unit,
    onNavigateToLogin: () -> Unit,
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
            Spacer(modifier = Modifier.height(40.dp))

            // Back button
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.Start
            ) {
                IconButton(onClick = onNavigateToLogin) {
                    Icon(
                        Icons.AutoMirrored.Outlined.ArrowBack,
                        contentDescription = "Back",
                        tint = TextPrimary
                    )
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Header
            Text(
                text = "✦",
                fontSize = 36.sp,
                color = CyanSecondary
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "Create Account",
                style = MaterialTheme.typography.headlineLarge,
                color = TextPrimary,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Join Gruha Alankara",
                style = MaterialTheme.typography.titleMedium,
                color = TextSecondary
            )

            Spacer(modifier = Modifier.height(32.dp))

            // Register card
            GlassCard(
                modifier = Modifier.fillMaxWidth()
            ) {
                GruhaTextField(
                    value = uiState.name,
                    onValueChange = onNameChanged,
                    label = "Full Name",
                    leadingIcon = Icons.Outlined.Person,
                    isError = uiState.nameError != null,
                    errorMessage = uiState.nameError,
                    imeAction = ImeAction.Next
                )

                Spacer(modifier = Modifier.height(16.dp))

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
                    imeAction = ImeAction.Next
                )

                Spacer(modifier = Modifier.height(16.dp))

                GruhaTextField(
                    value = uiState.confirmPassword,
                    onValueChange = onConfirmPasswordChanged,
                    label = "Confirm Password",
                    leadingIcon = Icons.Outlined.Lock,
                    isPassword = true,
                    isError = uiState.confirmPasswordError != null,
                    errorMessage = uiState.confirmPasswordError,
                    imeAction = ImeAction.Done,
                    onImeAction = onRegisterClick
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
                    text = "Create Account",
                    onClick = onRegisterClick,
                    isLoading = uiState.isLoading
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            // Login link
            Row(
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Already have an account? ",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondary
                )
                Text(
                    text = "Sign In",
                    style = MaterialTheme.typography.bodyMedium,
                    color = VioletPrimary,
                    fontWeight = FontWeight.SemiBold,
                    modifier = Modifier.clickable(onClick = onNavigateToLogin)
                )
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
