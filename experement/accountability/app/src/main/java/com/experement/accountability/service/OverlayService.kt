package com.experement.accountability.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.graphics.PixelFormat
import android.os.IBinder
import android.view.Gravity
import android.view.WindowManager
import androidx.compose.ui.platform.ComposeView
import androidx.core.app.NotificationCompat
import androidx.lifecycle.*
import androidx.savedstate.SavedStateRegistry
import androidx.savedstate.SavedStateRegistryController
import androidx.savedstate.SavedStateRegistryOwner
import androidx.savedstate.setViewTreeSavedStateRegistryOwner
import com.experement.accountability.ai.AiAgentHandler
import com.experement.accountability.ai.AiVerdict
import com.experement.accountability.data.SessionState
import com.experement.accountability.ui.overlay.ShameOverlayScreen
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class OverlayService : Service(), LifecycleOwner, ViewModelStoreOwner, SavedStateRegistryOwner {

    private lateinit var windowManager: WindowManager
    private var composeView: ComposeView? = null

    // Lifecycle requirements
    private val lifecycleRegistry = LifecycleRegistry(this)
    private val store = ViewModelStore()
    private val savedStateRegistryController = SavedStateRegistryController.create(this)

    // TODO: Read API key from secure storage; using placeholder for compilation 
    private val aiHandler = AiAgentHandler("PLACEHOLDER_KEY")
    private val scope = CoroutineScope(Dispatchers.Main)

    override val viewModelStore: ViewModelStore get() = store
    override val savedStateRegistry: SavedStateRegistry get() = savedStateRegistryController.savedStateRegistry
    override val lifecycle: Lifecycle get() = lifecycleRegistry

    override fun onCreate() {
        super.onCreate()
        savedStateRegistryController.performRestore(null)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_CREATE)
        windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val targetPackage = intent?.getStringExtra("target_package") ?: ""
        
        val notification = NotificationCompat.Builder(this, "gatekeeper_overlay")
            .setContentTitle("Gatekeeper Active")
            .setContentText("Intercepting...")
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setOngoing(true)
            .build()
            
        startForeground(1, notification)
        
        if (composeView == null) {
            showOverlay(targetPackage)
        }
        
        return START_NOT_STICKY
    }

    private fun showOverlay(targetPackage: String) {
        composeView = ComposeView(this).apply {
            setViewTreeLifecycleOwner(this@OverlayService)
            setViewTreeViewModelStoreOwner(this@OverlayService)
            setViewTreeSavedStateRegistryOwner(this@OverlayService)

            setContent {
                ShameOverlayScreen(
                    targetPackage = targetPackage,
                    onCancel = { removeOverlayAndStop() },
                    onSubmit = { justification ->
                        scope.launch {
                            val verdict = aiHandler.judge(targetPackage, justification)
                            handleVerdict(targetPackage, verdict)
                        }
                    }
                )
            }
        }

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_NOT_TOUCH_MODAL or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.CENTER
            // We need focus to type in the TextField!
            flags = WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN or WindowManager.LayoutParams.FLAG_DIM_BEHIND
            dimAmount = 0.9f
        }

        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_START)
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_RESUME)
        windowManager.addView(composeView, params)
    }

    private fun handleVerdict(pkg: String, verdict: AiVerdict) {
        when (verdict) {
            is AiVerdict.Approved -> {
                SessionState.approveApp(pkg, verdict.timeLimitMinutes)
                // Apply friction module here
                val frictionManager = com.experement.accountability.friction.FrictionManager(this)
                frictionManager.applyAllFriction()
                removeOverlayAndStop()
            }
            is AiVerdict.Denied -> {
                removeOverlayAndStop()
            }
            is AiVerdict.Timeout -> {
                removeOverlayAndStop()
            }
        }
    }

    private fun removeOverlayAndStop() {
        composeView?.let {
            windowManager.removeView(it)
            composeView = null
        }
        stopSelf()
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            "gatekeeper_overlay",
            "Gatekeeper Overlay",
            NotificationManager.IMPORTANCE_LOW
        )
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    override fun onDestroy() {
        super.onDestroy()
        lifecycleRegistry.handleLifecycleEvent(Lifecycle.Event.ON_DESTROY)
        store.clear()
        composeView?.let {
            if (it.isAttachedToWindow) {
                windowManager.removeView(it)
            }
            composeView = null
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
