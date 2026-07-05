package com.finbuddy.connector.data.repository

import android.util.Log
import com.finbuddy.connector.data.local.PreferencesManager
import com.finbuddy.connector.data.model.LoginRequest
import com.finbuddy.connector.data.model.LoginResponse
import com.finbuddy.connector.data.model.RefreshTokenRequest
import com.finbuddy.connector.data.model.UserResponse
import com.finbuddy.connector.data.remote.ApiService
import com.finbuddy.connector.utils.Result
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val preferencesManager: PreferencesManager
) {
    companion object {
        private const val TAG = "AuthRepository"
    }

    val isLoggedIn: Flow<Boolean> = preferencesManager.isLoggedIn
    val userEmail: Flow<String?> = preferencesManager.userEmail

    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return try {
            Log.d(TAG, "Attempting login for: $email")
            val response = apiService.login(LoginRequest(email, password))
            
            if (response.isSuccessful && response.body() != null) {
                val loginResponse = response.body()!!
                Log.d(TAG, "Login successful, saving tokens")
                
                // Save auth data (tokens only from login response)
                preferencesManager.saveAuthData(
                    accessToken = loginResponse.accessToken,
                    refreshToken = loginResponse.refreshToken,
                    userId = "", // Will be fetched from /users/me
                    email = email // Use the email from login request
                )
                
                // Fetch user details to get user ID
                try {
                    val userResponse = apiService.getCurrentUser()
                    if (userResponse.isSuccessful && userResponse.body() != null) {
                        val user = userResponse.body()!!
                        preferencesManager.saveAuthData(
                            accessToken = loginResponse.accessToken,
                            refreshToken = loginResponse.refreshToken,
                            userId = user.id,
                            email = user.email
                        )
                        Log.d(TAG, "User details fetched: ${user.id}")
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Failed to fetch user details", e)
                }
                
                Result.Success(loginResponse)
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Login failed"
                Log.e(TAG, "Login failed: $errorMessage")
                Result.Error(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Login error", e)
            Result.Error(e)
        }
    }

    suspend fun refreshToken(): Result<String> {
        return try {
            val refreshToken = preferencesManager.getRefreshToken()
                ?: return Result.Error(Exception("No refresh token available"))

            Log.d(TAG, "Refreshing token")
            val response = apiService.refreshToken(RefreshTokenRequest(refreshToken))
            
            if (response.isSuccessful && response.body() != null) {
                val tokenResponse = response.body()!!
                preferencesManager.updateAccessToken(tokenResponse.accessToken)
                Log.d(TAG, "Token refreshed successfully")
                Result.Success(tokenResponse.accessToken)
            } else {
                Log.e(TAG, "Token refresh failed")
                Result.Error(Exception("Token refresh failed"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Token refresh error", e)
            Result.Error(e)
        }
    }

    suspend fun getCurrentUser(): Result<UserResponse> {
        return try {
            val response = apiService.getCurrentUser()
            
            if (response.isSuccessful && response.body() != null) {
                Result.Success(response.body()!!)
            } else {
                Result.Error(Exception("Failed to get user info"))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Get user error", e)
            Result.Error(e)
        }
    }

    suspend fun logout() {
        Log.d(TAG, "Logging out")
        preferencesManager.logout()
    }
}
