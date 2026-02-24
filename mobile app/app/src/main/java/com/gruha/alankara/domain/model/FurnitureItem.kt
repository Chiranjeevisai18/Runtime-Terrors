package com.gruha.alankara.domain.model

import androidx.compose.ui.graphics.Color
import com.gruha.alankara.ui.theme.VioletPrimary
import com.gruha.alankara.ui.theme.CyanSecondary
import com.gruha.alankara.ui.theme.SuccessGreen
import com.gruha.alankara.ui.theme.WarningAmber
import com.gruha.alankara.ui.theme.ErrorRed

data class FurnitureItem(
    val id: String,
    val name: String,
    val modelFileName: String,
    val thumbnailColor: Color,
    val category: FurnitureCategory = FurnitureCategory.GENERAL,
    val defaultScale: Float = 0.5f
)

enum class FurnitureCategory {
    SEATING, TABLE, LIGHTING, STORAGE, GENERAL
}

// Pre-defined furniture catalog for MVP (geometric placeholders)
object FurnitureCatalog {
    val items = listOf(
        // SEATING
        FurnitureItem(
            id = "sheen_sofa_01",
            name = "Sheen Velvet Sofa",
            modelFileName = "sheen_sofa.glb",
            thumbnailColor = VioletPrimary,
            category = FurnitureCategory.SEATING,
            defaultScale = 0.5f
        ),
        FurnitureItem(
            id = "accent_chair_01",
            name = "Sheen Accent Chair",
            modelFileName = "sheen_chair.glb",
            thumbnailColor = SuccessGreen,
            category = FurnitureCategory.SEATING,
            defaultScale = 0.35f
        ),
        // TABLES & SURFACES
        FurnitureItem(
            id = "gaming_desk_01",
            name = "Gaming Desk & Set",
            modelFileName = "gaming_set_and_desk.glb",
            thumbnailColor = VioletPrimary,
            category = FurnitureCategory.TABLE,
            defaultScale = 0.5f
        ),
        FurnitureItem(
            id = "pc_setup_01",
            name = "Modern PC Setup",
            modelFileName = "modern_pc_desk_setup_-_3d_model.glb",
            thumbnailColor = CyanSecondary,
            category = FurnitureCategory.TABLE,
            defaultScale = 0.5f
        ),
        FurnitureItem(
            id = "wooden_crate_01",
            name = "Rustic Crate",
            modelFileName = "wooden_crate.glb",
            thumbnailColor = WarningAmber,
            category = FurnitureCategory.STORAGE,
            defaultScale = 0.4f
        ),
        // LIGHTING
        FurnitureItem(
            id = "lantern_01",
            name = "Antique Lantern",
            modelFileName = "lantern_lamp.glb",
            thumbnailColor = WarningAmber,
            category = FurnitureCategory.LIGHTING,
            defaultScale = 0.3f
        ),
        FurnitureItem(
            id = "candle_01",
            name = "Hurricane Candle",
            modelFileName = "candle_holder.glb",
            thumbnailColor = SuccessGreen,
            category = FurnitureCategory.LIGHTING,
            defaultScale = 0.25f
        ),
        // DECOR & GENERAL
        FurnitureItem(
            id = "camera_01",
            name = "Antique Camera",
            modelFileName = "antique_camera.glb",
            thumbnailColor = CyanSecondary,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.2f
        ),
        FurnitureItem(
            id = "boombox_01",
            name = "Retro Boombox",
            modelFileName = "boombox.glb",
            thumbnailColor = VioletPrimary,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.3f
        ),
        FurnitureItem(
            id = "toy_car_01",
            name = "Vintage Toy Car",
            modelFileName = "toy_car.glb",
            thumbnailColor = ErrorRed,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.15f
        ),
        FurnitureItem(
            id = "avocado_01",
            name = "Plush Avocado",
            modelFileName = "avocado.glb",
            thumbnailColor = SuccessGreen,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.15f
        ),
        FurnitureItem(
            id = "olives_01",
            name = "Olive Dish",
            modelFileName = "olive_dish.glb",
            thumbnailColor = WarningAmber,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.2f
        ),
        FurnitureItem(
            id = "bottle_01",
            name = "Glass Water Bottle",
            modelFileName = "water_bottle.glb",
            thumbnailColor = CyanSecondary,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.25f
        ),
        FurnitureItem(
            id = "helmet_01",
            name = "Explorer Helmet",
            modelFileName = "damaged_helmet.glb",
            thumbnailColor = ErrorRed,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.25f
        ),
        FurnitureItem(
            id = "corset_01",
            name = "Design Mockup",
            modelFileName = "corset.glb",
            thumbnailColor = VioletPrimary,
            category = FurnitureCategory.GENERAL,
            defaultScale = 0.3f
        )
    )
}
