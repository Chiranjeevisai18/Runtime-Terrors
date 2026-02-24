package com.gruha.alankara.ui.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.gruha.alankara.data.repository.AuthRepository
import com.gruha.alankara.data.repository.AuthResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AuthUiState(
    val isLoading: Boolean = false,
    val isLoggedIn: Boolean = false,
    val email: String = "",
    val password: String = "",
    val name: String = "",
    val confirmPassword: String = "",
    val errorMessage: String? = null,
    val emailError: String? = null,
    val passwordError: String? = null,
    val nameError: String? = null,
    val confirmPasswordError: String? = null
)

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    init {
        _uiState.update { it.copy(isLoggedIn = authRepository.isLoggedIn()) }
    }

    fun onEmailChanged(email: String) {
        _uiState.update { it.copy(email = email, emailError = null, errorMessage = null) }
    }

    fun onPasswordChanged(password: String) {
        _uiState.update { it.copy(password = password, passwordError = null, errorMessage = null) }
    }

    fun onNameChanged(name: String) {
        _uiState.update { it.copy(name = name, nameError = null, errorMessage = null) }
    }

    fun onConfirmPasswordChanged(confirmPassword: String) {
        _uiState.update {
            it.copy(confirmPassword = confirmPassword, confirmPasswordError = null, errorMessage = null)
        }
    }

    fun login() {
        if (!validateLoginFields()) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = authRepository.login(_uiState.value.email, _uiState.value.password)) {
                is AuthResult.Success -> {
                    _uiState.update { it.copy(isLoading = false, isLoggedIn = true) }
                }
                is AuthResult.Error -> {
                    _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
                }
            }
        }
    }

    fun register() {
        if (!validateRegisterFields()) return

        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            when (val result = authRepository.register(
                _uiState.value.name,
                _uiState.value.email,
                _uiState.value.password
            )) {
                is AuthResult.Success -> {
                    _uiState.update { it.copy(isLoading = false, isLoggedIn = true) }
                }
                is AuthResult.Error -> {
                    _uiState.update { it.copy(isLoading = false, errorMessage = result.message) }
                }
            }
        }
    }

    fun logout() {
        authRepository.logout()
        _uiState.update {
            AuthUiState(isLoggedIn = false)
        }
    }

    fun clearError() {
        _uiState.update { it.copy(errorMessage = null) }
    }

    private fun validateLoginFields(): Boolean {
        var isValid = true
        val state = _uiState.value

        if (state.email.isBlank() || !android.util.Patterns.EMAIL_ADDRESS.matcher(state.email).matches()) {
            _uiState.update { it.copy(emailError = "Please enter a valid email") }
            isValid = false
        }

        if (state.password.isBlank() || state.password.length < 6) {
            _uiState.update { it.copy(passwordError = "Password must be at least 6 characters") }
            isValid = false
        }

        return isValid
    }

    private fun validateRegisterFields(): Boolean {
        var isValid = validateLoginFields()
        val state = _uiState.value

        if (state.name.isBlank()) {
            _uiState.update { it.copy(nameError = "Name is required") }
            isValid = false
        }

        if (state.confirmPassword != state.password) {
            _uiState.update { it.copy(confirmPasswordError = "Passwords do not match") }
            isValid = false
        }

        return isValid
    }
}
