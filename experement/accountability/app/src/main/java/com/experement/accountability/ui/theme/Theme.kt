package com.experement.accountability.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable

@Composable
fun AccountabilityTheme(content: @Composable () -> Unit) {
    val colorScheme = darkColorScheme() // Force dark mode for now as per "strict" aesthetic
    MaterialTheme(
        colorScheme = colorScheme,
        content = content
    )
}
