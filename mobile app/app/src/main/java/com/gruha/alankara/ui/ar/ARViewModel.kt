package com.gruha.alankara.ui.ar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.remote.dto.DesignObjectDto
import com.gruha.alankara.data.remote.dto.LayoutAnalysisRequest
import com.gruha.alankara.data.remote.dto.RoomAnalysisResponse
import com.gruha.alankara.data.remote.dto.SaveDesignRequest
import com.gruha.alankara.data.remote.dto.Vector3Dto
import com.gruha.alankara.data.repository.AiRepository
import com.gruha.alankara.data.repository.DesignRepository
import com.gruha.alankara.data.repository.FurnitureRepository
import com.gruha.alankara.domain.model.FurnitureItem
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class PlacedObject(
    val id: String,
    val furniture: FurnitureItem,
    val anchorId: String? = null,
    val position: Vector3Dto = Vector3Dto(0f, 0f, 0f),
    val rotation: Float = 0f,
    val scale: Float = 1f
)

data class ARUiState(
    val isPlaneDetected: Boolean = false,
    val isTracking: Boolean = false,
    val trackingMessage: String = "Point your device at the floor to detect surfaces",
    val availableFurniture: List<FurnitureItem> = emptyList(),
    val selectedFurniture: FurnitureItem? = null,
    val placedObjects: List<PlacedObject> = emptyList(),
    val selectedPlacedObject: PlacedObject? = null,
    val objectCount: Int = 0,
    val maxObjects: Int = 20,
    val showFurniturePanel: Boolean = true,
    
    // AI Analysis State
    val isAnalyzing: Boolean = false,
    val aiDescription: String? = null,
    val recommendations: List<String> = emptyList(),
    val aiErrorMessage: String? = null,
    val roomAnalysis: RoomAnalysisResponse? = null,
    
    // Save State
    val isSavingDesign: Boolean = false,
    val lastSaveMessage: String? = null,
    val isReconstructing: Boolean = false,
    
    // Layout Analysis State
    val isAnalyzingLayout: Boolean = false,
    val clutterScore: Double = 0.0,
    val layoutSuggestions: List<String> = emptyList()
)

@HiltViewModel
class ARViewModel @Inject constructor(
    private val furnitureRepository: FurnitureRepository,
    private val aiRepository: AiRepository,
    private val designRepository: DesignRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ARUiState())
    val uiState: StateFlow<ARUiState> = _uiState.asStateFlow()

    init {
        loadFurniture()
    }

    private fun loadFurniture() {
        val furniture = furnitureRepository.getAvailableFurniture()
        _uiState.update {
            it.copy(
                availableFurniture = furniture,
                selectedFurniture = furniture.firstOrNull()
            )
        }
    }

    fun selectFurniture(furniture: FurnitureItem) {
        _uiState.update { it.copy(selectedFurniture = furniture) }
    }

    fun onPlaneDetected() {
        _uiState.update {
            it.copy(
                isPlaneDetected = true,
                isTracking = true,
                trackingMessage = "Surface detected! Tap to place furniture"
            )
        }
    }

    fun onTrackingUpdated(isTracking: Boolean) {
        _uiState.update {
            it.copy(
                isTracking = isTracking,
                trackingMessage = if (isTracking) {
                    if (it.isPlaneDetected) "Surface detected! Tap to place furniture"
                    else "Scanning for surfaces..."
                } else {
                    "Tracking lost. Move device slowly"
                }
            )
        }
    }

    fun onObjectPlaced(placedObject: PlacedObject) {
        _uiState.update {
            it.copy(
                placedObjects = it.placedObjects + placedObject,
                objectCount = it.objectCount + 1
            )
        }
    }

    fun selectPlacedObject(placedObject: PlacedObject?) {
        _uiState.update { it.copy(selectedPlacedObject = placedObject) }
    }

    fun removeSelectedObject() {
        val selected = _uiState.value.selectedPlacedObject ?: return
        _uiState.update {
            it.copy(
                placedObjects = it.placedObjects.filter { obj -> obj.id != selected.id },
                selectedPlacedObject = null,
                objectCount = it.objectCount - 1
            )
        }
    }

    fun resetScene() {
        _uiState.update {
            it.copy(
                placedObjects = emptyList(),
                selectedPlacedObject = null,
                objectCount = 0
            )
        }
    }

    fun toggleFurniturePanel() {
        _uiState.update { it.copy(showFurniturePanel = !it.showFurniturePanel) }
    }

    fun toggleFurniturePanel(visible: Boolean) {
        _uiState.update { it.copy(showFurniturePanel = visible) }
    }

    fun canPlaceMore(): Boolean {
        return _uiState.value.objectCount < _uiState.value.maxObjects
    }

    fun analyzeRoom(imageBytes: ByteArray) {
        viewModelScope.launch {
            _uiState.update { it.copy(isAnalyzing = true, aiErrorMessage = null) }
            val result = aiRepository.analyzeRoom(imageBytes)
            result.onSuccess { response ->
                _uiState.update { 
                    it.copy(
                        isAnalyzing = false,
                        aiDescription = response.description,
                        roomAnalysis = response,
                        recommendations = response.recommendedItems.map { item -> item.modelId }
                    )
                }
            }.onFailure { error ->
                _uiState.update { 
                    it.copy(
                        isAnalyzing = false,
                        aiErrorMessage = error.message ?: "Failed to analyze room"
                    )
                }
            }
        }
    }

    fun saveDesign(name: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSavingDesign = true, lastSaveMessage = null) }
            
            val objectsDto = _uiState.value.placedObjects.map { obj ->
                DesignObjectDto(
                    modelId = obj.furniture.id,
                    position = obj.position,
                    rotation = obj.rotation,
                    scale = obj.scale
                )
            }
            
            val request = SaveDesignRequest(name = name, objects = objectsDto)
            val result = designRepository.saveDesign(request)
            
            result.onSuccess {
                _uiState.update { it.copy(isSavingDesign = false, lastSaveMessage = "Design saved successfully!") }
            }.onFailure { error ->
                _uiState.update { it.copy(isSavingDesign = false, lastSaveMessage = "Error: ${error.message}") }
            }
        }
    }

    fun loadDesign(designId: Long) {
        viewModelScope.launch {
            _uiState.update { it.copy(isReconstructing = true) }
            
            // Try local first
            val localDesign = designRepository.getDesignById(designId)
            if (localDesign != null) {
                try {
                    val objectsDto = com.google.gson.Gson().fromJson(
                        localDesign.anchorsJson,
                        Array<DesignObjectDto>::class.java
                    ).toList()
                    
                    val placedObjects = objectsDto.mapNotNull { dto ->
                        val furniture = furnitureRepository.getAvailableFurniture().find { it.id == dto.modelId }
                        if (furniture != null) {
                            PlacedObject(
                                id = java.util.UUID.randomUUID().toString(),
                                furniture = furniture,
                                position = dto.position,
                                rotation = dto.rotation,
                                scale = dto.scale
                            )
                        } else null
                    }
                    
                    _uiState.update {
                        it.copy(
                            placedObjects = placedObjects,
                            objectCount = placedObjects.size,
                            isReconstructing = false
                        )
                    }
                } catch (e: Exception) {
                    _uiState.update { it.copy(isReconstructing = false) }
                }
            } else {
                _uiState.update { it.copy(isReconstructing = false) }
            }
        }
    }

    fun analyzeLayout() {
        viewModelScope.launch {
            _uiState.update { it.copy(isAnalyzingLayout = true) }
            
            val objectsDto = _uiState.value.placedObjects.map { obj ->
                DesignObjectDto(
                    modelId = obj.furniture.id,
                    position = obj.position,
                    rotation = obj.rotation,
                    scale = obj.scale
                )
            }
            
            val request = LayoutAnalysisRequest(objects = objectsDto)
            aiRepository.analyzeLayout(request).onSuccess { response ->
                _uiState.update { 
                    it.copy(
                        isAnalyzingLayout = false,
                        clutterScore = response.clutterScore,
                        layoutSuggestions = response.suggestions
                    )
                }
            }.onFailure {
                _uiState.update { it.copy(isAnalyzingLayout = false) }
            }
        }
    }

    fun clearLayoutAnalysis() {
        _uiState.update { it.copy(clutterScore = 0.0, layoutSuggestions = emptyList()) }
    }

    fun clearSaveMessage() {
        _uiState.update { it.copy(lastSaveMessage = null) }
    }
    
    fun clearAiResults() {
        _uiState.update { it.copy(aiDescription = null, recommendations = emptyList(), aiErrorMessage = null) }
    }
}
