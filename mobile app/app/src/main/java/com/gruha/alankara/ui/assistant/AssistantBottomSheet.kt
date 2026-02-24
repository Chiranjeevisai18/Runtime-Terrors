package com.gruha.alankara.ui.assistant

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.gruha.alankara.data.remote.dto.AssistantChatRequest
import com.gruha.alankara.data.remote.dto.AssistantChatResponse
import com.gruha.alankara.ui.theme.*
import com.mikepenz.markdown.m3.Markdown

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssistantBottomSheet(
    contextId: String?,
    roomType: String?,
    detectedObjects: List<String>,
    currentFurniture: List<String>,
    styleTheme: String = "modern",
    onDismiss: () -> Unit,
    viewModel: AssistantViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val sheetState = rememberModalBottomSheetState()

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = DeepSlate,
        dragHandle = { BottomSheetDefaults.DragHandle(color = SurfaceElevated2) }
    ) {
        Column(
            modifier = Modifier
                .fillMaxHeight(0.7f)
                .padding(bottom = 16.dp)
        ) {
            // Chat Header
            Text(
                text = "Assistant Intelligence",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimary,
                modifier = Modifier.padding(24.dp)
            )

            // Messages List
            LazyColumn(
                modifier = Modifier
                    .weight(1f)
                    .padding(horizontal = 20.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(uiState.messages) { message ->
                    ChatBubble(message)
                }
                if (uiState.isLoading) {
                    item {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp).padding(4.dp),
                                color = CyanSecondary,
                                strokeWidth = 2.dp
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text("Analyzing room context...", style = MaterialTheme.typography.labelSmall, color = TextSecondary)
                        }
                    }
                }
            }

            // Input Area
            Row(
                modifier = Modifier
                    .padding(16.dp)
                    .fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextField(
                    value = uiState.currentInput,
                    onValueChange = viewModel::onInputChanged,
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(24.dp)),
                    placeholder = { Text("Ask design advice...", color = TextSecondary) },
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = SurfaceElevated1,
                        unfocusedContainerColor = SurfaceElevated1,
                        focusedIndicatorColor = Color.Transparent,
                        unfocusedIndicatorColor = Color.Transparent
                    ),
                    maxLines = 3
                )
                
                Spacer(modifier = Modifier.width(8.dp))
                
                IconButton(
                    onClick = { 
                        viewModel.sendMessage(
                            contextId = contextId,
                            roomType = roomType,
                            detectedObjects = detectedObjects,
                            currentFurniture = currentFurniture,
                            styleTheme = styleTheme
                        ) 
                    },
                    enabled = uiState.currentInput.isNotEmpty() && !uiState.isLoading,
                    colors = IconButtonDefaults.iconButtonColors(
                        containerColor = VioletPrimary,
                        disabledContainerColor = SurfaceElevated2
                    )
                ) {
                    Icon(Icons.AutoMirrored.Filled.Send, contentDescription = "Send", tint = TextPrimary)
                }
            }
        }
    }
}

@Composable
private fun ChatBubble(message: Message) {
    val alignment = if (message.isUser) Alignment.End else Alignment.Start
    val bgColor = if (message.isUser) VioletPrimary.copy(alpha = 0.8f) else SurfaceElevated1
    val textColor = TextPrimary

    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = alignment
    ) {
        Surface(
            color = bgColor,
            shape = RoundedCornerShape(
                topStart = 16.dp,
                topEnd = 16.dp,
                bottomStart = if (message.isUser) 16.dp else 4.dp,
                bottomEnd = if (message.isUser) 4.dp else 16.dp
            )
        ) {
            if (message.isUser) {
                Text(
                    text = message.text,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp),
                    color = textColor,
                    fontSize = 14.sp
                )
            } else {
                Markdown(
                    content = message.text,
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 10.dp)
                )
            }
        }
    }
}
