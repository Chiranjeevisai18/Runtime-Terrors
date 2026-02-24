package com.gruha.alankara.ui.assistant

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.remote.dto.AssistantChatRequest
import com.gruha.alankara.data.repository.AssistantRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class Message(
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

data class AssistantUiState(
    val messages: List<Message> = listOf(
        Message("Hello! I'm your AI Interior Design Assistant. How can I help you with your room today?", false)
    ),
    val isLoading: Boolean = false,
    val currentInput: String = "",
    val actionSuggestion: String? = null
)

@HiltViewModel
class AssistantViewModel @Inject constructor(
    private val repository: AssistantRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AssistantUiState())
    val uiState: StateFlow<AssistantUiState> = _uiState.asStateFlow()

    fun onInputChanged(input: String) {
        _uiState.update { it.copy(currentInput = input) }
    }

    fun sendMessage(
        contextId: String?,
        roomType: String?, 
        detectedObjects: List<String>, 
        currentFurniture: List<String>,
        styleTheme: String = "modern"
    ) {
        val messageText = _uiState.value.currentInput.trim()
        if (messageText.isEmpty()) return

        // Add user message to UI
        val userMsg = Message(messageText, true)
        _uiState.update { state ->
            val updatedMessages = state.messages + userMsg
            // Keep only last 10 messages (5 pairs of user-assistant if strictly paired)
            // But requirement says "last 5 messages" in history. 
            // I'll take last 5 as total messages for strict compliance if that's the intent, 
            // or last 5 pairs. I'll stick to last 5 total for safety.
            val limitedMessages = if (updatedMessages.size > 5) updatedMessages.takeLast(5) else updatedMessages
            
            state.copy(
                messages = limitedMessages,
                currentInput = "",
                isLoading = true,
                actionSuggestion = null
            )
        }

        viewModelScope.launch {
            val request = AssistantChatRequest(
                contextId = contextId,
                userMessage = messageText,
                roomType = roomType,
                detectedObjects = detectedObjects,
                currentFurniture = currentFurniture,
                styleTheme = styleTheme
            )
            
            repository.chat(request).onSuccess { response ->
                val assistantMsg = Message(response.text, false)
                _uiState.update { state ->
                    val updatedMessages = state.messages + assistantMsg
                    val limitedMessages = if (updatedMessages.size > 5) updatedMessages.takeLast(5) else updatedMessages
                    
                    state.copy(
                        messages = limitedMessages,
                        isLoading = false,
                        actionSuggestion = response.suggestedAction
                    )
                }
            }.onFailure { error ->
                val errorMsg = Message("I'm having trouble connecting to my creative brain right now. Try again?", false)
                _uiState.update { state ->
                    val updatedMessages = state.messages + errorMsg
                    val limitedMessages = if (updatedMessages.size > 5) updatedMessages.takeLast(5) else updatedMessages
                    
                    state.copy(
                        messages = limitedMessages,
                        isLoading = false
                    )
                }
            }
        }
    }

    fun clearAction() {
        _uiState.update { it.copy(actionSuggestion = null) }
    }
}
