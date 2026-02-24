package com.gruha.alankara.ui.ar.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gruha.alankara.ui.theme.*

@Composable
fun StyleThemePanel(
    palette: List<Color>,
    selectedColor: Color?,
    onColorSelected: (Color) -> Unit,
    visible: Boolean,
    recommendedStyle: String? = null,
    onDismiss: () -> Unit
) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(initialOffsetY = { -it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { -it }) + fadeOut(),
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 20.dp)
            .padding(top = 80.dp)
    ) {
        Surface(
            color = DeepSlate.copy(alpha = 0.9f),
            shape = RoundedCornerShape(24.dp),
            border = BorderStroke(1.dp, SurfaceElevated2),
            tonalElevation = 8.dp
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "AI Style Theme",
                            style = MaterialTheme.typography.labelLarge,
                            color = TextSecondary
                        )
                        if (recommendedStyle != null) {
                            Text(
                                text = recommendedStyle,
                                style = MaterialTheme.typography.titleMedium,
                                color = CyanSecondary,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                    
                    TextButton(onClick = onDismiss) {
                        Text("Close", color = ErrorRed)
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                    contentPadding = PaddingValues(bottom = 8.dp)
                ) {
                    items(palette) { color ->
                        ColorCircle(
                            color = color,
                            isSelected = color == selectedColor,
                            onClick = { onColorSelected(color) }
                        )
                    }
                }
                
                Text(
                    text = "Select a color to tint the furniture material",
                    style = MaterialTheme.typography.labelSmall,
                    color = TextSecondary.copy(alpha = 0.7f),
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
private fun ColorCircle(
    color: Color,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(52.dp)
            .clip(CircleShape)
            .background(color)
            .border(
                width = if (isSelected) 3.dp else 0.dp,
                color = TextPrimary,
                shape = CircleShape
            )
            .clickable(onClick = onClick)
    )
}
