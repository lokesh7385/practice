package com.experement.accountability.ui

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.experement.accountability.service.GatekeeperAccessibilityService
import com.experement.accountability.ui.theme.AccountabilityTheme
import com.experement.accountability.util.PackageUtils.isAccessibilityServiceEnabled

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AccountabilityTheme {
                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    GatekeeperAppContent(modifier = Modifier.padding(innerPadding))
                }
            }
        }
    }
}

@Composable
fun GatekeeperAppContent(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    var hasOverlayPermission by remember { mutableStateOf(Settings.canDrawOverlays(context)) }
    var hasAccessibilityPermission by remember { 
        mutableStateOf(isAccessibilityServiceEnabled(context, GatekeeperAccessibilityService::class.java)) 
    }

    // Simple refresh mechanism for permissions
    LaunchedEffect(Unit) {
        hasOverlayPermission = Settings.canDrawOverlays(context)
        hasAccessibilityPermission = isAccessibilityServiceEnabled(context, GatekeeperAccessibilityService::class.java)
    }

    if (hasOverlayPermission && hasAccessibilityPermission) {
        // Main Dashboard would go here
        Column(
            modifier = modifier.fillMaxSize().padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Gatekeeper Active", style = MaterialTheme.typography.headlineMedium)
            Spacer(modifier = Modifier.height(16.dp))
            Text("All permissions granted. The Accessibility Service is monitoring for distractions.", style = MaterialTheme.typography.bodyMedium)
        }
    } else {
        PermissionScreen(
            missingOverlay = !hasOverlayPermission,
            missingAccessibility = !hasAccessibilityPermission,
            modifier = modifier
        )
    }
}

@Composable
fun PermissionScreen(
    missingOverlay: Boolean, 
    missingAccessibility: Boolean,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    
    Column(
        modifier = modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text("Permissions Required", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))
        Text("This app needs special permissions to enforce focus.", style = MaterialTheme.typography.bodyMedium)
        Spacer(modifier = Modifier.height(32.dp))

        if (missingOverlay) {
            Button(
                onClick = {
                    val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:${context.packageName}"))
                    context.startActivity(intent)
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Grant 'Display Over Other Apps'")
            }
            Spacer(modifier = Modifier.height(16.dp))
        }

        if (missingAccessibility) {
            Button(
                onClick = {
                    val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                    context.startActivity(intent)
                },
                modifier = Modifier.fillMaxWidth(),
                colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.tertiary)
            ) {
                Text("Enable 'Accountability' Accessibility")
            }
        }
    }
}
