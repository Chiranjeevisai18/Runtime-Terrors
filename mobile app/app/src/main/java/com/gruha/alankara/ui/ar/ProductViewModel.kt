package com.gruha.alankara.ui.ar

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.remote.api.ProductApiService
import com.gruha.alankara.data.remote.dto.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class ProductSearchState {
    object Idle : ProductSearchState()
    object Loading : ProductSearchState()
    data class Success(val productsMap: Map<String, List<ProductDto>>) : ProductSearchState()
    data class Error(val message: String) : ProductSearchState()
}

sealed class BookingState {
    object Idle : BookingState()
    object Processing : BookingState()
    data class NeedsInfo(val question: String, val sessionId: String?) : BookingState()
    data class Success(val orderId: String) : BookingState()
    data class Fallback(val redirectUrl: String) : BookingState()
    data class Error(val message: String) : BookingState()
}

@HiltViewModel
class ProductViewModel @Inject constructor(
    private val productApiService: ProductApiService
) : ViewModel() {

    private val _searchState = MutableStateFlow<ProductSearchState>(ProductSearchState.Idle)
    val searchState: StateFlow<ProductSearchState> = _searchState.asStateFlow()

    private val _bookingState = MutableStateFlow<BookingState>(BookingState.Idle)
    val bookingState: StateFlow<BookingState> = _bookingState.asStateFlow()

    fun searchProductsForCart(queries: List<String>) {
        if (queries.isEmpty()) {
            _searchState.value = ProductSearchState.Success(emptyMap())
            return
        }
        
        viewModelScope.launch {
            _searchState.value = ProductSearchState.Loading
            try {
                // Fetch products for all unique queries concurrently
                val resultsMap = mutableMapOf<String, List<ProductDto>>()
                queries.forEach { query ->
                    try {
                        val response = productApiService.searchProducts(ProductSearchRequest(query))
                        if (response.results.isNotEmpty()) {
                            resultsMap[query] = response.results
                        }
                    } catch (e: Exception) {
                        // Log individual failure but continue with others
                    }
                }
                
                if (resultsMap.isEmpty()) {
                     _searchState.value = ProductSearchState.Error("No products found for any items in the cart.")
                } else {
                    _searchState.value = ProductSearchState.Success(resultsMap)
                }
            } catch (e: Exception) {
                _searchState.value = ProductSearchState.Error(e.message ?: "Cart search failed")
            }
        }
    }

    fun autoBook(productUrl: String) {
        viewModelScope.launch {
            _bookingState.value = BookingState.Processing
            try {
                val response = productApiService.autoBook(BookingRequest(productUrl))
                handleBookingResponse(response)
            } catch (e: Exception) {
                _bookingState.value = BookingState.Error(e.message ?: "Booking failed")
            }
        }
    }

    fun resumeBooking(sessionId: String, answer: String) {
        viewModelScope.launch {
            _bookingState.value = BookingState.Processing
            try {
                val response = productApiService.resumeBooking(BookingResumeRequest(sessionId, answer))
                handleBookingResponse(response)
            } catch (e: Exception) {
                _bookingState.value = BookingState.Error(e.message ?: "Resume failed")
            }
        }
    }

    private fun handleBookingResponse(response: BookingResponse) {
        when (response.status) {
            "SUCCESS" -> {
                _bookingState.value = BookingState.Success(response.orderId ?: "UNKNOWN")
            }
            "INFO_REQUIRED" -> {
                _bookingState.value = BookingState.NeedsInfo(
                    response.question ?: "Please provide more info",
                    response.sessionId
                )
            }
            "FALLBACK" -> {
                _bookingState.value = BookingState.Fallback(response.redirectUrl ?: "")
            }
            else -> {
                _bookingState.value = BookingState.Error(response.reason ?: "Unknown error")
            }
        }
    }

    fun resetBookingState() {
        _bookingState.value = BookingState.Idle
    }
}
