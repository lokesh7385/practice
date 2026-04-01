package com.experement.accountability.ui.overlay

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun ShameOverlayScreen(
    targetPackage: String,
    onCancel: () -> Unit,
    onSubmit: (String) -> Unit
) {
    var justification by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color.Black.copy(alpha = 0.95f))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "HOLD ON.",
            color = Color.Red,
            fontSize = 48.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Text(
            text = "You're trying to open $targetPackage.",
            color = Color.White,
            fontSize = 20.sp,
            textAlign = TextAlign.Center
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = "Is this really necessary right now? The Gatekeeper requires a legitimate, specific justification.",
            color = Color.LightGray,
            fontSize = 16.sp,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = justification,
            onValueChange = { justification = it },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                unfocusedTextColor = Color.White,
                focusedTextColor = Color.White,
                unfocusedBorderColor = Color.DarkGray,
                focusedBorderColor = MaterialTheme.colorScheme.primary
            ),
            placeholder = { Text("I need to reply to a DM from...") },
            minLines = 3
        )

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = { onSubmit(justification) },
            modifier = Modifier.fillMaxWidth(),
            enabled = justification.isNotBlank()
        ) {
            Text("Request Unlock")
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = onCancel) {
            Text("Nevermind", color = Color.Gray)
        }
    }
}
