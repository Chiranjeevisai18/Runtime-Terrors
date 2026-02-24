package com.gruha.alankara.ui.ar.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoFixHigh
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Save
import androidx.compose.material.icons.filled.ViewInAr
import androidx.compose.material.icons.filled.Chat
import androidx.compose.material.icons.filled.Palette
import androidx.compose.material.icons.filled.Straighten
import androidx.compose.material.icons.outlined.Logout
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gruha.alankara.ui.theme.*

@Composable
fun ARControlsOverlay(
    isPlaneDetected: Boolean,
    trackingMessage: String,
    objectCount: Int,
    maxObjects: Int,
    hasSelectedObject: Boolean,
    onRemoveSelected: () -> Unit,
    onResetScene: () -> Unit,
    onAnalyzeRoom: () -> Unit,
    onSaveDesign: () -> Unit,
    onToggleFurniture: () -> Unit,
    onOpenAssistant: () -> Unit,
    onOpenStyleTheme: () -> Unit,
    onAnalyzeLayout: () -> Unit,
    onOpenCart: () -> Unit,
    onLogout: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(modifier = modifier.fillMaxSize()) {
        // Top bar with status and logout
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .statusBarsPadding()
                .padding(horizontal = 16.dp, vertical = 8.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Tracking status pill
            Surface(
                shape = RoundedCornerShape(20.dp),
                color = CardDark.copy(alpha = 0.85f),
                shadowElevation = 4.dp
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    // Status dot
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .background(
                                color = if (isPlaneDetected) SuccessGreen else WarningAmber,
                                shape = CircleShape
                            )
                    )
                    Text(
                        text = trackingMessage,
                        style = MaterialTheme.typography.labelSmall,
                        color = TextSecondary,
                        maxLines = 1
                    )
                }
            }

            // Logout fab
            SmallFloatingActionButton(
                onClick = onLogout,
                containerColor = CardDark.copy(alpha = 0.85f),
                contentColor = TextSecondary
            ) {
                Icon(
                    Icons.Outlined.Logout,
                    contentDescription = "Logout",
                    modifier = Modifier.size(18.dp)
                )
            }
        }

        // Object count badge
        if (objectCount > 0) {
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = CardDark.copy(alpha = 0.85f),
                modifier = Modifier
                    .align(Alignment.TopCenter)
                    .statusBarsPadding()
                    .padding(top = 56.dp)
            ) {
                Text(
                    text = "$objectCount / $maxObjects objects",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (objectCount >= maxObjects) ErrorRed else CyanSecondary,
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                )
            }
        }

        // Right side FAB column
        Column(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .padding(end = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Global Cart Button
            if (objectCount > 0) {
                ARCartButton(
                    count = objectCount,
                    onClick = onOpenCart
                )
                
                Spacer(modifier = Modifier.height(16.dp))
            }

            // Toggle furniture panel
            ARFab(
                icon = Icons.Default.ViewInAr,
                contentDescription = "Furniture",
                onClick = onToggleFurniture,
                containerColor = VioletPrimary
            )

            // AI Analyze Room
            ARFab(
                icon = Icons.Default.AutoFixHigh,
                contentDescription = "Analyze Room",
                onClick = onAnalyzeRoom,
                containerColor = CyanSecondary
            )

            // Save Design
            ARFab(
                icon = Icons.Default.Save,
                contentDescription = "Save Design",
                onClick = onSaveDesign,
                containerColor = SuccessGreen
            )

            // AI Assistant
            ARFab(
                icon = Icons.Default.Chat,
                contentDescription = "AI Assistant",
                onClick = onOpenAssistant,
                containerColor = VioletLight
            )

            // Style Theme
            ARFab(
                icon = Icons.Default.Palette,
                contentDescription = "Style Theme",
                onClick = onOpenStyleTheme,
                containerColor = WarningAmber
            )

            // Layout Analysis
            ARFab(
                icon = Icons.Default.Straighten,
                contentDescription = "Analyze Layout",
                onClick = onAnalyzeLayout,
                containerColor = SurfaceElevated2
            )

            // Remove selected
            AnimatedVisibility(
                visible = hasSelectedObject,
                enter = scaleIn() + fadeIn(),
                exit = scaleOut() + fadeOut()
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    ARFab(
                        icon = Icons.Default.Delete,
                        contentDescription = "Remove",
                        onClick = onRemoveSelected,
                        containerColor = ErrorRed
                    )
                }
            }

            // Reset scene
            AnimatedVisibility(
                visible = objectCount > 0,
                enter = scaleIn() + fadeIn(),
                exit = scaleOut() + fadeOut()
            ) {
                ARFab(
                    icon = Icons.Default.Refresh,
                    contentDescription = "Reset Scene",
                    onClick = onResetScene,
                    containerColor = CardDark.copy(alpha = 0.85f)
                )
            }
        }
    }
}

@Composable
private fun ARFab(
    icon: ImageVector,
    contentDescription: String,
    onClick: () -> Unit,
    containerColor: androidx.compose.ui.graphics.Color
) {
    SmallFloatingActionButton(
        onClick = onClick,
        containerColor = containerColor,
        contentColor = TextPrimary,
        shape = CircleShape,
        elevation = FloatingActionButtonDefaults.elevation(
            defaultElevation = 6.dp,
            pressedElevation = 3.dp
        )
    ) {
        Icon(
            icon,
            contentDescription = contentDescription,
            modifier = Modifier.size(20.dp)
        )
    }
}

@Composable
private fun ARCartButton(
    count: Int,
    onClick: () -> Unit
) {
    Box(contentAlignment = Alignment.TopEnd) {
        FloatingActionButton(
            onClick = onClick,
            containerColor = DeepSlate,
            contentColor = TextPrimary,
            elevation = FloatingActionButtonDefaults.elevation(
                defaultElevation = 8.dp,
                pressedElevation = 4.dp
            )
        ) {
            Icon(
                imageVector = Icons.Default.ShoppingCart,
                contentDescription = "Open Cart"
            )
        }
        
        // Badge
        Surface(
            shape = CircleShape,
            color = CyanSecondary,
            modifier = Modifier
                .offset(x = 8.dp, y = (-8).dp)
                .size(24.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Text(
                    text = count.toString(),
                    color = DeepSlate,
                    style = MaterialTheme.typography.labelSmall,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

