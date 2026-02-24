package com.gruha.alankara.ui.ar.components

import androidx.compose.animation.*
import androidx.compose.foundation.background
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.gruha.alankara.domain.model.FurnitureItem
import com.gruha.alankara.ui.theme.*

@Composable
fun FurnitureCarousel(
    furniture: List<FurnitureItem>,
    selectedItem: FurnitureItem?,
    onItemSelected: (FurnitureItem) -> Unit,
    visible: Boolean,
    recommendations: List<String> = emptyList(),
    modifier: Modifier = Modifier
) {
    AnimatedVisibility(
        visible = visible,
        enter = slideInVertically(initialOffsetY = { it }) + fadeIn(),
        exit = slideOutVertically(targetOffsetY = { it }) + fadeOut(),
        modifier = modifier
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(
                            DeepSlate.copy(alpha = 0f),
                            DeepSlate.copy(alpha = 0.85f),
                            DeepSlate.copy(alpha = 0.95f)
                        )
                    )
                )
                .padding(vertical = 16.dp)
        ) {
            Text(
                text = "Select Furniture",
                style = MaterialTheme.typography.labelLarge,
                color = TextSecondary,
                modifier = Modifier.padding(horizontal = 20.dp, vertical = 4.dp)
            )

            Spacer(modifier = Modifier.height(8.dp))

            LazyRow(
                contentPadding = PaddingValues(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(furniture) { item ->
                    FurnitureCard(
                        item = item,
                        isSelected = item.id == selectedItem?.id,
                        isRecommended = recommendations.contains(item.id),
                        onClick = { onItemSelected(item) }
                    )
                }
            }
        }
    }
}

@Composable
private fun FurnitureCard(
    item: FurnitureItem,
    isSelected: Boolean,
    isRecommended: Boolean,
    onClick: () -> Unit
) {
    val borderColor = if (isSelected) VioletPrimary else CardDarkVariant
    val backgroundColor = if (isSelected) CardDark else SurfaceElevated1

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier
            .clip(RoundedCornerShape(16.dp))
            .border(
                width = if (isSelected) 2.dp else 1.dp,
                color = borderColor,
                shape = RoundedCornerShape(16.dp)
            )
            .background(backgroundColor)
            .clickable(onClick = onClick)
            .padding(12.dp)
            .width(72.dp)
    ) {
        // Color indicator circle (placeholder for model thumbnail)
        Box(
            modifier = Modifier
                .size(48.dp)
                .clip(CircleShape)
                .background(
                    brush = Brush.radialGradient(
                        colors = listOf(
                            item.thumbnailColor.copy(alpha = 0.8f),
                            item.thumbnailColor.copy(alpha = 0.4f)
                        )
                    )
                ),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = item.name.first().toString(),
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimary,
                fontWeight = FontWeight.Bold
            )
        }

        if (isRecommended) {
            Spacer(modifier = Modifier.height(4.dp))
            Surface(
                shape = RoundedCornerShape(4.dp),
                color = CyanSecondary,
                modifier = Modifier.height(14.dp)
            ) {
                Text(
                    text = "Recommended",
                    style = MaterialTheme.typography.labelSmall.copy(fontSize = 7.sp),
                    color = DeepSlate,
                    modifier = Modifier.padding(horizontal = 4.dp),
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = item.name,
            style = MaterialTheme.typography.labelMedium,
            color = if (isSelected) VioletLight else TextSecondary,
            textAlign = TextAlign.Center,
            maxLines = 1
        )
    }
}
