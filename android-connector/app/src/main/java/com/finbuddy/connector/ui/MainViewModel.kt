package com.finbuddy.connector.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.finbuddy.connector.data.local.PreferencesManager
import com.finbuddy.connector.data.repository.AuthRepository
import com.finbuddy.connector.data.repository.SmsRepository
import com.finbuddy.connector.utils.Result
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class SyncState {
    object Idle : SyncState()
    object Syncing : SyncState()
    data class Success(val count: Int) : SyncState()
    data class Error(val message: String) : SyncState()
}

@HiltViewModel
class MainViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val smsRepository: SmsRepository,
    private val preferencesManager: PreferencesManager
) : ViewModel() {

    val isLoggedIn = authRepository.isLoggedIn
    val userEmail = authRepository.userEmail
    val lastSyncTime = preferencesManager.lastSyncTime
    val autoSyncEnabled = preferencesManager.autoSyncEnabled

    private val _syncState = MutableStateFlow<SyncState>(SyncState.Idle)
    val syncState: StateFlow<SyncState> = _syncState.asStateFlow()

    fun syncNow() {
        viewModelScope.launch {
            _syncState.value = SyncState.Syncing

            when (val result = smsRepository.performFullSync()) {
                is Result.Success -> {
                    _syncState.value = SyncState.Success(result.data)
                }
                is Result.Error -> {
                    _syncState.value = SyncState.Error(
                        result.exception.message ?: "Sync failed"
                    )
                }
            }
        }
    }

    fun setAutoSync(enabled: Boolean) {
        viewModelScope.launch {
            preferencesManager.setAutoSyncEnabled(enabled)
        }
    }

    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
        }
    }
}
