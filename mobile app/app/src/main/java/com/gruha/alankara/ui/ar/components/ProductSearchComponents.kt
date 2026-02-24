package com.gruha.alankara.ui.ar.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalUriHandler
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.gruha.alankara.data.remote.dto.ProductDto
import com.gruha.alankara.ui.ar.BookingState
import com.gruha.alankara.ui.ar.ProductSearchState
import com.gruha.alankara.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductSearchBottomSheet(
    searchState: ProductSearchState,
    onBookProduct: (ProductDto) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = CardDark,
        tonalElevation = 8.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(bottom = 32.dp)
        ) {
            Text(
                text = "Discover Real Furniture",
                style = MaterialTheme.typography.headlineSmall,
                color = TextPrimary,
                modifier = Modifier.padding(horizontal = 24.dp, vertical = 16.dp)
            )

            when (searchState) {
                is ProductSearchState.Loading -> {
                    Box(modifier = Modifier.fillMaxWidth().height(300.dp), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = CyanSecondary)
                    }
                }
                is ProductSearchState.Success -> {
                    if (searchState.productsMap.isEmpty()) {
                        EmptyState("No matching products found in cart.")
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxWidth(),
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(24.dp)
                        ) {
                            searchState.productsMap.forEach { (query, products) ->
                                item {
                                    Text(
                                        text = "Matching '$query'",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = CyanSecondary,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(bottom = 8.dp)
                                    )
                                }
                                items(products) { product ->
                                    ProductCard(
                                        product = product,
                                        onBookProduct = onBookProduct
                                    )
                                    Spacer(modifier = Modifier.height(12.dp))
                                }
                            }
                        }
                    }
                }
                is ProductSearchState.Error -> {
                    EmptyState("Error: ${searchState.message}")
                }
                else -> {}
            }
        }
    }
}

@Composable
fun ProductCard(
    product: ProductDto,
    onBookProduct: (ProductDto) -> Unit
) {
    Surface(
        shape = RoundedCornerShape(16.dp),
        color = SurfaceElevated1,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier
                .padding(12.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            AsyncImage(
                model = product.imageUrl,
                contentDescription = product.title,
                modifier = Modifier
                    .size(100.dp)
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = product.title,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimary,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis
                )
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = product.price ?: "N/A",
                        style = MaterialTheme.typography.titleLarge,
                        color = CyanSecondary,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    if (product.rating != null) {
                       Icon(Icons.Default.Star, contentDescription = null, tint = WarningAmber, modifier = Modifier.size(14.dp))
                       Text(text = product.rating, color = TextSecondary, style = MaterialTheme.typography.bodySmall)
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                Button(
                    onClick = { onBookProduct(product) },
                    colors = ButtonDefaults.buttonColors(containerColor = SuccessGreen),
                    modifier = Modifier.height(36.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 0.dp)
                ) {
                    Icon(Icons.Default.ShoppingCart, contentDescription = null, modifier = Modifier.size(14.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Auto Book", style = MaterialTheme.typography.labelMedium)
                }
            }
        }
    }
}

@Composable
fun BookingStatusDialog(
    bookingState: BookingState,
    onAnswerInfo: (String) -> Unit,
    onDismiss: () -> Unit
) {
    val uriHandler = LocalUriHandler.current

    AlertDialog(
        onDismissRequest = { if (bookingState !is BookingState.Processing) onDismiss() },
        containerColor = CardDark,
        title = {
            Text(
                when (bookingState) {
                    is BookingState.Processing -> "Booking in Progress"
                    is BookingState.NeedsInfo -> "Info Required"
                    is BookingState.Success -> "Booking Successful!"
                    is BookingState.Fallback -> "Secure Redirection"
                    else -> "Booking Status"
                }
            )
        },
        text = {
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                when (bookingState) {
                    is BookingState.Processing -> {
                        CircularProgressIndicator(color = VioletPrimary)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Alankara AI is communicating with the vendor...", textAlign = androidx.compose.ui.text.style.TextAlign.Center)
                    }
                    is BookingState.NeedsInfo -> {
                        Text(bookingState.question, fontWeight = FontWeight.SemiBold)
                        Spacer(modifier = Modifier.height(16.dp))
                        var answer by remember { mutableStateOf("") }
                        OutlinedTextField(
                            value = answer,
                            onValueChange = { answer = it },
                            placeholder = { Text("e.g. Size M, Beige") },
                            modifier = Modifier.fillMaxWidth()
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { onAnswerInfo(answer) },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Submit Info")
                        }
                    }
                    is BookingState.Success -> {
                        Icon(Icons.Default.ShoppingCart, contentDescription = null, tint = SuccessGreen, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("Order Placed: ${bookingState.orderId}")
                    }
                    is BookingState.Fallback -> {
                        Icon(Icons.Default.Info, contentDescription = null, tint = WarningAmber, modifier = Modifier.size(48.dp))
                        Spacer(modifier = Modifier.height(16.dp))
                        Text("To ensure security, please complete the final steps in your browser.")
                    }
                    is BookingState.Error -> {
                        Text("Error: ${bookingState.message}", color = ErrorRed)
                    }
                    else -> {}
                }
            }
        },
        confirmButton = {
            if (bookingState is BookingState.Fallback) {
                Button(onClick = { 
                    uriHandler.openUri(bookingState.redirectUrl)
                    onDismiss()
                }) {
                    Text("Open Browser")
                }
            } else if (bookingState is BookingState.Success || bookingState is BookingState.Error) {
                TextButton(onClick = onDismiss) {
                    Text("Dismiss")
                }
            }
        }
    )
}

@Composable
fun EmptyState(message: String) {
    Box(modifier = Modifier.fillMaxWidth().height(200.dp), contentAlignment = Alignment.Center) {
        Text(text = message, color = TextTertiary)
    }
}
