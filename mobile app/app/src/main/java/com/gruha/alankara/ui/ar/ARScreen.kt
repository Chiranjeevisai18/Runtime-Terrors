package com.gruha.alankara.ui.ar

import io.github.sceneview.ar.node.AnchorNode
import com.gruha.alankara.data.remote.dto.Vector3Dto
import java.util.UUID
import android.graphics.Bitmap
import android.os.Handler
import android.os.Looper
import android.view.PixelCopy
import androidx.compose.ui.graphics.toArgb
import com.gruha.alankara.data.remote.dto.DesignObjectDto

import android.Manifest
import android.content.pm.PackageManager
import android.view.MotionEvent
import android.view.ScaleGestureDetector
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Error
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.google.ar.core.Config
import com.google.ar.core.TrackingState
import com.gruha.alankara.ui.ar.components.ARControlsOverlay
import com.gruha.alankara.ui.ar.components.FurnitureCarousel
import com.gruha.alankara.ui.theme.*
import io.github.sceneview.ar.ARSceneView
import io.github.sceneview.node.ModelNode
import java.io.ByteArrayOutputStream
import com.gruha.alankara.ui.assistant.AssistantBottomSheet
import com.gruha.alankara.ui.assistant.AssistantViewModel
import com.gruha.alankara.ui.ar.components.LayoutSuggestionsPanel
import com.gruha.alankara.ui.ar.components.StyleThemePanel
import com.gruha.alankara.ui.ar.ColorThemeViewModel
import io.github.sceneview.math.Position
import io.github.sceneview.math.Rotation
import io.github.sceneview.math.Scale
import com.gruha.alankara.ui.ar.components.ProductSearchBottomSheet
import com.gruha.alankara.ui.ar.components.BookingStatusDialog
import com.gruha.alankara.ui.ar.ProductSearchState
import com.gruha.alankara.ui.ar.BookingState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ARScreen(
    designId: Long? = null,
    onLogout: () -> Unit,
    viewModel: ARViewModel = hiltViewModel(),
    assistantViewModel: AssistantViewModel = hiltViewModel(),
    colorThemeViewModel: ColorThemeViewModel = hiltViewModel(),
    productViewModel: ProductViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val themeState by colorThemeViewModel.uiState.collectAsState()
    val productSearchState by productViewModel.searchState.collectAsStateWithLifecycle()
    val bookingState by productViewModel.bookingState.collectAsStateWithLifecycle()
    
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    
    // UI State for dialogs
    var showSaveDialog by remember { mutableStateOf(false) }
    var designName by remember { mutableStateOf("") }
    var showAiResultSheet by remember { mutableStateOf(false) }
    var showRecommendationSheet by remember { mutableStateOf(false) }
    var showAssistant by remember { mutableStateOf(false) }
    var showStyleTheme by remember { mutableStateOf(false) }
    var showLayoutAnalysis by remember { mutableStateOf(false) }
    var showProductSearch by remember { mutableStateOf(false) }
    var showBookingStatus by remember { mutableStateOf(false) }
    
    val sheetState = rememberModalBottomSheetState()

    // Camera permission state
    var hasCameraPermission by remember {
        mutableStateOf(
            context.checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
        )
    }
    var showPermissionRationale by remember { mutableStateOf(false) }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
        if (!granted) showPermissionRationale = true
    }

    LaunchedEffect(Unit) {
        if (!hasCameraPermission) {
            permissionLauncher.launch(Manifest.permission.CAMERA)
        }
        // Load design if ID is provided
        designId?.let { viewModel.loadDesign(it) }
    }

    if (!hasCameraPermission) {
        CameraPermissionScreen(
            showRationale = showPermissionRationale,
            onRequestPermission = {
                permissionLauncher.launch(Manifest.permission.CAMERA)
            }
        )
        return
    }

    // AR Scene
    Box(modifier = Modifier.fillMaxSize()) {
        var arSceneView by remember { mutableStateOf<ARSceneView?>(null) }
        var scaleDetector by remember { mutableStateOf<ScaleGestureDetector?>(null) }
        
        // Track the currently selected node for transformations
        var selectedModelNode by remember { mutableStateOf<ModelNode?>(null) }

        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { ctx ->
                ARSceneView(ctx).apply {
                    configureSession { session, config ->
                        config.planeFindingMode = Config.PlaneFindingMode.HORIZONTAL
                        config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
                    }

                    onSessionUpdated = { session, frame ->
                        if (frame.camera.trackingState == TrackingState.TRACKING) {
                            viewModel.onTrackingUpdated(true)
                            val planes = session.getAllTrackables(com.google.ar.core.Plane::class.java)
                            if (planes.any { it.trackingState == TrackingState.TRACKING }) {
                                viewModel.onPlaneDetected()
                            }
                        } else {
                            viewModel.onTrackingUpdated(false)
                        }
                    }

                    onTouchEvent = { event: MotionEvent, hitResult ->
                        // Handle scale gestures
                        scaleDetector?.onTouchEvent(event)
                        
                        val selectedModel = uiState.selectedFurniture
                        
                        // Simple rotation with horizontal scroll when model selected
                        if (event.pointerCount == 1 && selectedModelNode != null) {
                            if (event.action == MotionEvent.ACTION_MOVE) {
                                val deltaX = event.historySize.let { if (it > 0) event.getHistoricalX(0, 0) - event.x else 0f }
                                selectedModelNode?.let { node ->
                                    node.rotation = node.rotation.plus(io.github.sceneview.math.Rotation(0f, deltaX, 0f))
                                }
                            }
                        }

                        if (event.action == MotionEvent.ACTION_UP && uiState.isPlaneDetected && viewModel.canPlaceMore() && selectedModel != null) {
                            val frame = session?.update()
                            if (frame != null) {
                                val arHits = frame.hitTest(event)
                                val planeHit = arHits.firstOrNull { hit ->
                                    val trackable = hit.trackable
                                    trackable is com.google.ar.core.Plane && trackable.isPoseInPolygon(hit.hitPose)
                                }
                                if (planeHit != null) {
                                    val anchor = planeHit.createAnchor()
                                    val anchorNode = AnchorNode(engine = this.engine, anchor = anchor)
                                    
                                    // Snap to center of plane if close
                                    val snapThreshold = 0.15f // 15cm
                                    val hitPose = planeHit.hitPose
                                    val trackablePlane = planeHit.trackable as com.google.ar.core.Plane
                                    val centerPose = trackablePlane.centerPose
                                    
                                    val distToCenter = Math.sqrt(
                                        Math.pow((hitPose.tx() - centerPose.tx()).toDouble(), 2.0) +
                                        Math.pow((hitPose.tz() - centerPose.tz()).toDouble(), 2.0)
                                    )
                                    
                                    val finalPosition = if (distToCenter < snapThreshold) {
                                        Position(0f, 0f, 0f) // Snap to plane local origin
                                    } else {
                                        Position(hitPose.tx(), 0f, hitPose.tz())
                                    }

                                    val newObjId = java.util.UUID.randomUUID().toString()
                                    val placedObj = PlacedObject(
                                        id = newObjId,
                                        furniture = selectedModel,
                                        anchorId = anchor.hashCode().toString()
                                    )
                                    viewModel.onObjectPlaced(placedObj)

                                    val modelNode = ModelNode(
                                        modelInstance = modelLoader.createModelInstance( assetFileLocation = "models/${selectedModel.modelFileName}" ),
                                        scaleToUnits = selectedModel.defaultScale
                                    ).apply {
                                        name = "models/${selectedModel.modelFileName}"
                                        position = finalPosition
                                        onSingleTapConfirmed = {
                                            selectedModelNode = this
                                            viewModel.selectPlacedObject(placedObj)
                                            true
                                        }
                                    }
                                    anchorNode.addChildNode(modelNode)
                                    addChildNode(anchorNode)
                                    selectedModelNode = modelNode
                                }
                            }
                        }
                        true
                    }
                    
                    // Initialize scale detector
                    scaleDetector = ScaleGestureDetector(context, object : ScaleGestureDetector.SimpleOnScaleGestureListener() {
                        override fun onScale(detector: ScaleGestureDetector): Boolean {
                            selectedModelNode?.let { node ->
                                node.scale = node.scale.times(detector.scaleFactor)
                            }
                            return true
                        }
                    })
                    
                    arSceneView = this
                }
            }
        )

        // Collision Detection & Scene Intelligence Loop
        LaunchedEffect(uiState.placedObjects.size) {
            while (true) {
                kotlinx.coroutines.delay(1000) // Check every 1s
                val view = arSceneView ?: continue
                val nodes = view.childNodes.filterIsInstance<AnchorNode>()
                    .flatMap { it.childNodes.filterIsInstance<ModelNode>() }
                
                for (i in nodes.indices) {
                    val nodeA = nodes[i]
                    var isColliding = false
                    for (j in nodes.indices) {
                        if (i == j) continue
                        val nodeB = nodes[j]
                        
                        val dist = Math.sqrt(
                            Math.pow((nodeA.worldPosition.x - nodeB.worldPosition.x).toDouble(), 2.0) +
                            Math.pow((nodeA.worldPosition.z - nodeB.worldPosition.z).toDouble(), 2.0)
                        )
                        
                        if (dist < 0.4) { // 40cm threshold for collision
                            isColliding = true
                            break
                        }
                    }
                    
                    nodeA.modelInstance?.materialInstances?.forEach { material ->
                        if (isColliding) {
                            material.setParameter("baseColorFactor", 1f, 0.2f, 0.2f, 1f) // Red tint
                        } else {
                            material.setParameter("baseColorFactor", 1f, 1f, 1f, 1f) // Default
                        }
                    }
                }
            }
        }

        // Scene Reconstruction Logic
        LaunchedEffect(uiState.isPlaneDetected, uiState.placedObjects) {
            val view = arSceneView ?: return@LaunchedEffect
            val session = view.session ?: return@LaunchedEffect
            
            if (uiState.isPlaneDetected && uiState.placedObjects.isNotEmpty()) {
                // Check if nodes already exist to avoid duplicates during reconstruction
                val currentAnchorCount = view.childNodes.filterIsInstance<AnchorNode>().size
                if (currentAnchorCount < uiState.placedObjects.size && uiState.isReconstructing.not()) {
                    // Try to find a plane to anchor the reconstructed items
                    val planes = session.getAllTrackables(com.google.ar.core.Plane::class.java)
                    val firstPlane = planes.firstOrNull { it.trackingState == TrackingState.TRACKING }
                    
                    if (firstPlane != null) {
                        uiState.placedObjects.forEach { obj ->
                            // Only spawn if not already in the scene (simplified check)
                            val alreadyPlaced = view.childNodes.filterIsInstance<AnchorNode>().any { 
                                it.childNodes.filterIsInstance<ModelNode>().any { mn -> mn.name == "models/${obj.furniture.modelFileName}" }
                            }
                            
                            if (!alreadyPlaced) {
                                val anchor = firstPlane.createAnchor(firstPlane.centerPose)
                                val anchorNode = AnchorNode(engine = view.engine, anchor = anchor)
                                val modelNode = ModelNode(
                                    modelInstance = view.modelLoader.createModelInstance( assetFileLocation = "models/${obj.furniture.modelFileName}" ),
                                    scaleToUnits = obj.furniture.defaultScale
                                ).apply {
                                    name = "models/${obj.furniture.modelFileName}"
                                    // Apply saved transforms
                                    position = Position(obj.position.x, obj.position.y, obj.position.z)
                                    rotation = Rotation(0f, obj.rotation, 0f)
                                    scale = Scale(obj.scale)
                                    
                                    onSingleTapConfirmed = {
                                        selectedModelNode = this
                                        viewModel.selectPlacedObject(obj)
                                        true
                                    }
                                }
                                anchorNode.addChildNode(modelNode)
                                view.addChildNode(anchorNode)
                            }
                        }
                    }
                }
            }
        }

        // Food carousel at bottom
        FurnitureCarousel(
            furniture = uiState.availableFurniture,
            selectedItem = uiState.selectedFurniture,
            onItemSelected = { viewModel.selectFurniture(it) },
            visible = uiState.showFurniturePanel,
            recommendations = uiState.recommendations,
            modifier = Modifier.align(Alignment.BottomCenter)
        )
        
        // AI Analyze & Save Handlers
        ARControlsOverlay(
            isPlaneDetected = uiState.isPlaneDetected,
            trackingMessage = uiState.trackingMessage,
            objectCount = uiState.objectCount,
            maxObjects = uiState.maxObjects,
            hasSelectedObject = uiState.selectedPlacedObject != null,
            onRemoveSelected = { viewModel.removeSelectedObject() },
            onResetScene = {
                viewModel.resetScene()
                arSceneView?.let { view ->
                    val nodesToRemove = view.childNodes.filterIsInstance<AnchorNode>()
                    nodesToRemove.forEach { node ->
                        view.removeChildNode(node)
                        node.destroy()
                    }
                }
            },
            onAnalyzeRoom = {
                arSceneView?.let { view ->
                    captureBitmapFromView(view) { bitmap ->
                        val stream = ByteArrayOutputStream()
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, stream)
                        viewModel.analyzeRoom(stream.toByteArray())
                        showAiResultSheet = true
                    }
                }
            },
            onSaveDesign = {
                showSaveDialog = true
            },
            onToggleFurniture = { viewModel.toggleFurniturePanel() },
            onOpenAssistant = { showAssistant = true },
            onOpenStyleTheme = {
                arSceneView?.let { view ->
                    captureBitmapFromView(view) { bitmap ->
                        val stream = ByteArrayOutputStream()
                        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, stream)
                        colorThemeViewModel.extractPalette(stream.toByteArray())
                        showStyleTheme = true
                    }
                }
            },
            onAnalyzeLayout = {
                viewModel.analyzeLayout()
                showLayoutAnalysis = true
            },
            onOpenCart = {
                val uniqueFurnitureNames = uiState.placedObjects.map { it.furniture.name }.distinct()
                if (uniqueFurnitureNames.isNotEmpty()) {
                    productViewModel.searchProductsForCart(uniqueFurnitureNames)
                }
                showProductSearch = true
            },
            onLogout = onLogout,
            modifier = Modifier.padding(bottom = 120.dp)
        )

        // Layout Analysis Suggestions
        if (showLayoutAnalysis && uiState.layoutSuggestions.isNotEmpty()) {
            LayoutSuggestionsPanel(
                clutterScore = uiState.clutterScore,
                suggestions = uiState.layoutSuggestions,
                onDismiss = { 
                    showLayoutAnalysis = false
                    viewModel.clearLayoutAnalysis()
                }
            )
        }

        // Style Theme Panel
        StyleThemePanel(
            palette = themeState.palette,
            selectedColor = themeState.selectedColor,
            visible = showStyleTheme,
            recommendedStyle = themeState.recommendedStyle,
            onColorSelected = { color ->
                colorThemeViewModel.selectColor(color)
                selectedModelNode?.let { node ->
                    // Dynamic material tinting
                    node.modelInstance?.materialInstances?.forEach { material ->
                        material.setParameter("baseColorFactor", color.red, color.green, color.blue, color.alpha)
                    }
                }
            },
            onDismiss = { showStyleTheme = false }
        )

        // Assistant Bottom Sheet
        if (showAssistant) {
            AssistantBottomSheet(
                contextId = uiState.roomAnalysis?.contextId,
                roomType = uiState.roomAnalysis?.roomType,
                detectedObjects = uiState.roomAnalysis?.detectedObjects ?: emptyList(),
                currentFurniture = uiState.placedObjects.map { it.furniture.name },
                styleTheme = themeState.recommendedStyle ?: "modern",
                onDismiss = { showAssistant = false },
                viewModel = assistantViewModel
            )
        }

        // AI Results Bottom Sheet
        if (showAiResultSheet && (uiState.aiDescription != null || uiState.isAnalyzing || uiState.aiErrorMessage != null)) {
            ModalBottomSheet(
                onDismissRequest = { 
                    showAiResultSheet = false
                    viewModel.clearAiResults()
                },
                sheetState = sheetState,
                containerColor = CardDark
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    if (uiState.isAnalyzing) {
                        CircularProgressIndicator(color = VioletPrimary)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Analyzing your room...", color = TextPrimary)
                    } else if (uiState.aiErrorMessage != null) {
                        Icon(
                            imageVector = Icons.Default.Error,
                            contentDescription = null,
                            tint = ErrorRed,
                            modifier = Modifier.size(48.dp)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.aiErrorMessage ?: "An unknown error occurred",
                            color = TextPrimary,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = { showAiResultSheet = false },
                            colors = ButtonDefaults.buttonColors(containerColor = SurfaceElevated2),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Dismiss", color = TextPrimary)
                        }
                    } else {
                        Text(
                            text = "AI Room Analysis",
                            style = MaterialTheme.typography.headlineSmall,
                            color = TextPrimary
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = uiState.aiDescription ?: "",
                            style = MaterialTheme.typography.bodyLarge,
                            color = TextSecondary,
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = { 
                                showAiResultSheet = false 
                                viewModel.toggleFurniturePanel(true)
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = CyanSecondary),
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("See Recommendations", color = DeepSlate)
                        }
                    }
                    Spacer(modifier = Modifier.height(48.dp))
                }
            }
        }

        // Save Design Dialog
        if (showSaveDialog) {
            AlertDialog(
                onDismissRequest = { showSaveDialog = false },
                title = { Text("Save Design") },
                text = {
                    Column {
                        Text("Enter a name for your design layout:")
                        Spacer(modifier = Modifier.height(8.dp))
                        TextField(
                            value = designName,
                            onValueChange = { designName = it },
                            placeholder = { Text("e.g. Living Room Dream") }
                        )
                    }
                },
                confirmButton = {
                    TextButton(onClick = {
                        viewModel.saveDesign(designName)
                        showSaveDialog = false
                    }) {
                        Text("Save")
                    }
                },
                dismissButton = {
                    TextButton(onClick = { showSaveDialog = false }) {
                        Text("Cancel")
                    }
                }
            )
        }
        
        // Save Success Snackbar
        LaunchedEffect(uiState.lastSaveMessage) {
            uiState.lastSaveMessage?.let {
                // You could use a snackbar host here, but for now just clear it
                viewModel.clearSaveMessage()
            }
        }

        // --- Phase 5: Product Discovery & Booking UI ---
        
        if (showProductSearch) {
            ProductSearchBottomSheet(
                searchState = productSearchState,
                onBookProduct = { product ->
                    showProductSearch = false
                    productViewModel.autoBook(product.url)
                    showBookingStatus = true
                },
                onDismiss = { showProductSearch = false }
            )
        }

        if (showBookingStatus) {
            BookingStatusDialog(
                bookingState = bookingState,
                onAnswerInfo = { answer ->
                    // Handle info resumption
                    if (bookingState is BookingState.NeedsInfo) {
                        val session = (bookingState as BookingState.NeedsInfo).sessionId
                        if (session != null) {
                            productViewModel.resumeBooking(session, answer)
                        }
                    }
                },
                onDismiss = { 
                    showBookingStatus = false 
                    productViewModel.resetBookingState()
                }
            )
        }
    }
}

private fun captureBitmapFromView(view: ARSceneView, onBitmapCaptured: (Bitmap) -> Unit) {
    val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)
    val locationOfViewInWindow = IntArray(2)
    view.getLocationInWindow(locationOfViewInWindow)
    
    try {
        PixelCopy.request(
            view,
            android.graphics.Rect(
                locationOfViewInWindow[0],
                locationOfViewInWindow[1],
                locationOfViewInWindow[0] + view.width,
                locationOfViewInWindow[1] + view.height
            ),
            bitmap,
            { copyResult ->
                if (copyResult == PixelCopy.SUCCESS) {
                    onBitmapCaptured(bitmap)
                }
            },
            Handler(Looper.getMainLooper())
        )
    } catch (e: Exception) {
        e.printStackTrace()
    }
}

@Composable
private fun CameraPermissionScreen(
    showRationale: Boolean,
    onRequestPermission: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DeepSlate),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(32.dp)
        ) {
            Text(
                text = "📷",
                style = MaterialTheme.typography.displayLarge
            )
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "Camera Permission Required",
                style = MaterialTheme.typography.headlineMedium,
                color = TextPrimary,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = "Gruha Alankara needs camera access to scan your room and place virtual furniture in AR.",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(32.dp))
            Button(
                onClick = onRequestPermission,
                colors = ButtonDefaults.buttonColors(containerColor = VioletPrimary),
                shape = RoundedCornerShape(14.dp)
            ) {
                Text("Grant Permission", color = TextPrimary)
            }
        }
    }
}
