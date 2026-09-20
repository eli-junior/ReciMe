package br.com.recime

import java.net.URI
import java.text.Normalizer

data class Ingredient(val name: String, val quantity: String = "")
data class Recipe(
    val id: Long = 0,
    val title: String,
    val ingredients: List<Ingredient>,
    val steps: List<String>,
    val source: String = DEMO_URL,
)

const val DEMO_URL = "https://www.instagram.com/p/DdC8Aw1RQU4/"

// Transcrição manual da legenda; não é resultado do Gemini.
fun demoRecipe() = Recipe(
    title = "Fraldinha com crosta de alho e batatas",
    ingredients = listOf(
        Ingredient("Fraldinha"), Ingredient("Sal"), Ingredient("Páprica defumada"),
        Ingredient("Pimenta-do-reino"), Ingredient("Batatas", "4 ou 5"),
        Ingredient("Azeite"), Ingredient("Orégano"), Ingredient("Cebola"),
        Ingredient("Alho", "5 dentes"), Ingredient("Manteiga para dourar o alho"),
        Ingredient("Farinha panko"), Ingredient("Queijo muçarela"),
        Ingredient("Salsinha e cebolinha"), Ingredient("Manteiga em ponto de pomada", "1/2 colher"),
    ),
    steps = listOf(
        "Tempere a fraldinha com sal, páprica defumada e pimenta-do-reino. Tempere as batatas separadamente com azeite, sal, páprica defumada e orégano.",
        "Forre a forma com cebola, coloque a carne e as batatas e cubra com papel-alumínio. Asse a 220 °C por 45 minutos.",
        "Retire o papel-alumínio e deixe no forno por mais 10 a 15 minutos.",
        "Doure os 5 dentes de alho na manteiga. Misture com farinha panko, muçarela, salsinha, cebolinha e 1/2 colher de manteiga em ponto de pomada.",
        "Coloque a mistura sobre a carne e leve para dourar por mais 10 minutos.",
    ),
)

fun validInstagramUrl(value: String): Boolean = runCatching {
    val uri = URI(value.trim())
    uri.scheme == "https" && uri.host in setOf("instagram.com", "www.instagram.com") &&
        uri.userInfo == null && uri.port in setOf(-1, 443) &&
        Regex("/(reel|reels|p)/[A-Za-z0-9_-]+/?").matches(uri.path ?: "")
}.getOrDefault(false)

private fun normalized(value: String) = Normalizer.normalize(value, Normalizer.Form.NFD)
    .replace(Regex("\\p{M}+"), "").lowercase(java.util.Locale.ROOT)

fun List<Recipe>.search(query: String) = filter { normalized(it.title).contains(normalized(query.trim())) }
