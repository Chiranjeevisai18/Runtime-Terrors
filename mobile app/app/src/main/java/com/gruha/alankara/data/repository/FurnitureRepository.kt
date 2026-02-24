package com.gruha.alankara.data.repository

import com.gruha.alankara.domain.model.FurnitureCatalog
import com.gruha.alankara.domain.model.FurnitureItem
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class FurnitureRepository @Inject constructor() {

    fun getAvailableFurniture(): List<FurnitureItem> {
        return FurnitureCatalog.items
    }

    fun getFurnitureById(id: String): FurnitureItem? {
        return FurnitureCatalog.items.find { it.id == id }
    }

    fun getFurnitureByCategory(
        category: com.gruha.alankara.domain.model.FurnitureCategory
    ): List<FurnitureItem> {
        return FurnitureCatalog.items.filter { it.category == category }
    }
}
