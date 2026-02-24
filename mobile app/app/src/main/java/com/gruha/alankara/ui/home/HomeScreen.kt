package com.gruha.alankara.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.gruha.alankara.data.remote.dto.DesignResponse
import com.gruha.alankara.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onNavigateToAR: (Long?) -> Unit,
    onLogout: () -> Unit,
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        containerColor = DeepSlate,
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("My Designs", color = TextPrimary, fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = DeepSlate),
                actions = {
                    IconButton(onClick = onLogout) {
                        Icon(Icons.Default.Logout, contentDescription = "Logout", tint = TextSecondary)
                    }
                }
            )
        },
        floatingActionButton = {
            LargeFloatingActionButton(
                onClick = { onNavigateToAR(null) },
                containerColor = VioletPrimary,
                contentColor = TextPrimary
            ) {
                Icon(Icons.Default.Add, contentDescription = "New Design")
            }
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            if (uiState.isLoading) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator(color = VioletPrimary)
                }
            } else if (uiState.designs.isEmpty()) {
                EmptyDesignsPlaceholder({ onNavigateToAR(null) })
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(uiState.designs) { design ->
                        DesignCard(
                            design = design,
                            onDelete = { viewModel.deleteDesign(design.id) },
                            onClick = { onNavigateToAR(design.id.toLong()) }
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DesignCard(
    design: DesignResponse,
    onDelete: () -> Unit,
    onClick: () -> Unit
) {
    Surface(
        color = CardDark,
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.fillMaxWidth().clickable { onClick() }
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = design.name,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimary,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "${design.objects.size} items • ${design.createdAt?.take(10) ?: "Just now"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            
            IconButton(onClick = onDelete) {
                Icon(Icons.Default.Delete, contentDescription = "Delete", tint = ErrorRed.copy(alpha = 0.7f))
            }
        }
    }
}

@Composable
private fun EmptyDesignsPlaceholder(onAction: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(120.dp)
                .background(
                    brush = Brush.radialGradient(listOf(VioletPrimary.copy(alpha = 0.2f), DeepSlate)),
                    shape = RoundedCornerShape(60.dp)
                ),
            contentAlignment = Alignment.Center
        ) {
            Text("✨", style = MaterialTheme.typography.displayMedium)
        }
        Spacer(modifier = Modifier.height(24.dp))
        Text(
            text = "No Designs Found",
            style = MaterialTheme.typography.headlineSmall,
            color = TextPrimary
        )
        Text(
            text = "Start by creating your first AR furniture layout!",
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondary,
            modifier = Modifier.padding(top = 8.dp)
        )
        Spacer(modifier = Modifier.height(32.dp))
        Button(
            onClick = onAction,
            colors = ButtonDefaults.buttonColors(containerColor = VioletPrimary),
            shape = RoundedCornerShape(12.dp)
        ) {
            Text("Create New Design", color = TextPrimary)
        }
    }
}
