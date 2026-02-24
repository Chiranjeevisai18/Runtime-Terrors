package com.gruha.alankara.ui.ar

import androidx.compose.ui.graphics.Color
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.repository.AiRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class ColorThemeUiState(
    val isExtracting: Boolean = false,
    val palette: List<Color> = emptyList(),
    val dominantColor: Color? = null,
    val recommendedStyle: String? = null,
    val selectedColor: Color? = null,
    val errorMessage: String? = null
)

@HiltViewModel
class ColorThemeViewModel @Inject constructor(
    private val aiRepository: AiRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ColorThemeUiState())
    val uiState: StateFlow<ColorThemeUiState> = _uiState.asStateFlow()

    fun extractPalette(imageBytes: ByteArray) {
        _uiState.update { it.copy(isExtracting = true, errorMessage = null) }
        
        viewModelScope.launch {
            aiRepository.extractColors(imageBytes).onSuccess { response ->
                val paletteColors = response.palette.map { hexToColor(it) }
                _uiState.update {
                    it.copy(
                        isExtracting = false,
                        palette = paletteColors,
                        dominantColor = hexToColor(response.dominantColor),
                        recommendedStyle = response.recommendedStyle
                    )
                }
            }.onFailure { error ->
                _uiState.update {
                    it.copy(
                        isExtracting = false,
                        errorMessage = "Failed to extract palette: ${error.message}"
                    )
                }
            }
        }
    }

    fun selectColor(color: Color) {
        _uiState.update { it.copy(selectedColor = color) }
    }

    fun clear() {
        _uiState.update { ColorThemeUiState() }
    }

    private fun hexToColor(hex: String): Color {
        return try {
            Color(android.graphics.Color.parseColor(hex))
        } catch (e: Exception) {
            Color.Gray
        }
    }
}
