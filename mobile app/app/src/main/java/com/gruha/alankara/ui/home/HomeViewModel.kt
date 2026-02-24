package com.gruha.alankara.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.remote.dto.DesignResponse
import com.gruha.alankara.data.repository.DesignRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val designs: List<DesignResponse> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val designRepository: DesignRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadDesigns()
    }

    fun loadDesigns() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val result = designRepository.getDesigns()
            result.onSuccess { designs ->
                _uiState.update { it.copy(isLoading = false, designs = designs) }
            }.onFailure { error ->
                _uiState.update { it.copy(isLoading = false, errorMessage = error.message) }
            }
        }
    }

    fun deleteDesign(id: Int) {
        viewModelScope.launch {
            val result = designRepository.deleteDesign(id)
            result.onSuccess {
                loadDesigns()
            }
        }
    }
}
