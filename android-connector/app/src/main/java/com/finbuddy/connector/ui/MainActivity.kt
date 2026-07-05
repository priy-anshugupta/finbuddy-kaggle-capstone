package com.finbuddy.connector.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.finbuddy.connector.databinding.ActivityMainBinding
import com.finbuddy.connector.sync.SmsSyncWorker
import com.finbuddy.connector.sync.SyncService
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.TimeUnit

@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    private val smsPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.entries.all { it.value }
        if (allGranted) {
            onPermissionsGranted()
        } else {
            showPermissionDeniedDialog()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        checkLoginStatus()
        setupUI()
        observeViewModel()
    }

    private fun checkLoginStatus() {
        lifecycleScope.launch {
            viewModel.isLoggedIn.collect { isLoggedIn ->
                if (!isLoggedIn) {
                    navigateToLogin()
                }
            }
        }
    }

    private fun setupUI() {
        binding.btnSyncNow.setOnClickListener {
            if (hasRequiredPermissions()) {
                viewModel.syncNow()
            } else {
                requestPermissions()
            }
        }

        binding.btnLogout.setOnClickListener {
            showLogoutDialog()
        }

        binding.switchAutoSync.setOnCheckedChangeListener { _, isChecked ->
            viewModel.setAutoSync(isChecked)
            if (isChecked) {
                schedulePeriodicSync()
            } else {
                cancelPeriodicSync()
            }
        }

        binding.btnGrantPermissions.setOnClickListener {
            requestPermissions()
        }
    }

    private fun observeViewModel() {
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                launch {
                    viewModel.userEmail.collect { email ->
                        binding.tvUserEmail.text = email ?: "Not logged in"
                    }
                }

                launch {
                    viewModel.lastSyncTime.collect { timestamp ->
                        binding.tvLastSync.text = if (timestamp > 0) {
                            "Last sync: ${formatTimestamp(timestamp)}"
                        } else {
                            "Never synced"
                        }
                    }
                }

                launch {
                    viewModel.autoSyncEnabled.collect { enabled ->
                        binding.switchAutoSync.isChecked = enabled
                    }
                }

                launch {
                    viewModel.syncState.collect { state ->
                        when (state) {
                            is SyncState.Idle -> {
                                binding.progressSync.visibility = View.GONE
                                binding.btnSyncNow.isEnabled = true
                                binding.tvSyncStatus.text = "Ready to sync"
                            }
                            is SyncState.Syncing -> {
                                binding.progressSync.visibility = View.VISIBLE
                                binding.btnSyncNow.isEnabled = false
                                binding.tvSyncStatus.text = "Syncing..."
                            }
                            is SyncState.Success -> {
                                binding.progressSync.visibility = View.GONE
                                binding.btnSyncNow.isEnabled = true
                                binding.tvSyncStatus.text = "Synced ${state.count} transactions"
                                Toast.makeText(
                                    this@MainActivity,
                                    "Synced ${state.count} transactions",
                                    Toast.LENGTH_SHORT
                                ).show()
                            }
                            is SyncState.Error -> {
                                binding.progressSync.visibility = View.GONE
                                binding.btnSyncNow.isEnabled = true
                                binding.tvSyncStatus.text = "Sync failed"
                                Toast.makeText(
                                    this@MainActivity,
                                    state.message,
                                    Toast.LENGTH_LONG
                                ).show()
                            }
                        }
                    }
                }
            }
        }
    }

    private fun hasRequiredPermissions(): Boolean {
        val smsPermission = ContextCompat.checkSelfPermission(
            this, Manifest.permission.READ_SMS
        ) == PackageManager.PERMISSION_GRANTED

        val notificationPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        } else true

        updatePermissionUI(smsPermission)
        return smsPermission && notificationPermission
    }

    private fun updatePermissionUI(hasPermission: Boolean) {
        binding.cardPermissions.visibility = if (hasPermission) View.GONE else View.VISIBLE
        binding.cardSync.visibility = if (hasPermission) View.VISIBLE else View.GONE
    }

    private fun requestPermissions() {
        val permissions = mutableListOf(
            Manifest.permission.READ_SMS,
            Manifest.permission.RECEIVE_SMS
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }

        smsPermissionLauncher.launch(permissions.toTypedArray())
    }

    private fun onPermissionsGranted() {
        updatePermissionUI(true)
        Toast.makeText(this, "Permissions granted!", Toast.LENGTH_SHORT).show()
        schedulePeriodicSync()
    }

    private fun showPermissionDeniedDialog() {
        AlertDialog.Builder(this)
            .setTitle("Permissions Required")
            .setMessage("SMS permission is required to read and sync your financial transactions. Please grant the permission to continue.")
            .setPositiveButton("Grant") { _, _ -> requestPermissions() }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun showLogoutDialog() {
        AlertDialog.Builder(this)
            .setTitle("Logout")
            .setMessage("Are you sure you want to logout?")
            .setPositiveButton("Logout") { _, _ ->
                viewModel.logout()
                cancelPeriodicSync()
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun schedulePeriodicSync() {
        val periodicWork = PeriodicWorkRequestBuilder<SmsSyncWorker>(
            6, TimeUnit.HOURS,
            15, TimeUnit.MINUTES
        ).build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            SmsSyncWorker.PERIODIC_WORK_NAME,
            ExistingPeriodicWorkPolicy.KEEP,
            periodicWork
        )
    }

    private fun cancelPeriodicSync() {
        WorkManager.getInstance(this).cancelUniqueWork(SmsSyncWorker.PERIODIC_WORK_NAME)
    }

    private fun navigateToLogin() {
        startActivity(Intent(this, LoginActivity::class.java))
        finish()
    }

    private fun formatTimestamp(timestamp: Long): String {
        val sdf = SimpleDateFormat("dd MMM yyyy, hh:mm a", Locale.getDefault())
        return sdf.format(Date(timestamp))
    }

    override fun onResume() {
        super.onResume()
        hasRequiredPermissions()
    }
}
