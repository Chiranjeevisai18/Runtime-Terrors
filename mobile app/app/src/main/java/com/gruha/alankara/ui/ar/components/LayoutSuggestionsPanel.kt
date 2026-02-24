package com.gruha.alankara.ui.ar.components

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.gruha.alankara.ui.theme.*

@Composable
fun LayoutSuggestionsPanel(
    clutterScore: Double,
    suggestions: List<String>,
    onDismiss: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        contentAlignment = Alignment.BottomCenter
    ) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 240.dp), // Position above bottom bar
            color = DeepSlate.copy(alpha = 0.95f),
            shape = RoundedCornerShape(20.dp),
            tonalElevation = 12.dp
        ) {
            Column(
                modifier = Modifier.padding(20.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Layout Intelligence",
                        style = MaterialTheme.typography.titleMedium,
                        color = TextPrimary,
                        fontWeight = FontWeight.Bold
                    )
                    
                    TextButton(onClick = onDismiss) {
                        Text("Dismiss", color = VioletLight)
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Clutter Meter
                Column {
                    Text(
                        text = "Clutter Score: ${(clutterScore * 100).toInt()}%",
                        style = MaterialTheme.typography.labelMedium,
                        color = if (clutterScore > 0.6) ErrorRed else TextSecondary
                    )
                    LinearProgressIndicator(
                        progress = { clutterScore.toFloat() },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(8.dp)
                            .padding(vertical = 4.dp),
                        color = if (clutterScore > 0.6) ErrorRed else CyanSecondary,
                        trackColor = SurfaceElevated1
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "AI Suggestions:",
                    style = MaterialTheme.typography.labelLarge,
                    color = TextSecondary
                )
                
                Spacer(modifier = Modifier.height(8.dp))

                suggestions.forEach { suggestion ->
                    Row(
                        modifier = Modifier.padding(vertical = 4.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Text(
                            text = "•",
                            color = CyanSecondary,
                            modifier = Modifier.padding(end = 8.dp)
                        )
                        Text(
                            text = suggestion,
                            style = MaterialTheme.typography.bodyMedium,
                            color = TextPrimary
                        )
                    }
                }
            }
        }
    }
}
