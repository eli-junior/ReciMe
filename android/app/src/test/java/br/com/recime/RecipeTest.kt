package br.com.recime

import org.junit.Assert.*
import org.junit.Test

class RecipeTest {
    @Test fun acceptsPostAndReelLinks() {
        assertTrue(validInstagramUrl(DEMO_URL))
        assertTrue(validInstagramUrl("https://instagram.com/reel/ABC/?igsh=test"))
    }
    @Test fun rejectsMisleadingHostsAndOtherProtocols() {
        listOf("https://instagram.com.evil.com/p/ABC/", "https://user@instagram.com/p/ABC/",
            "http://instagram.com/p/ABC/", "https://instagram.com/stories/ABC/", "not a url"
        ).forEach { assertFalse(it, validInstagramUrl(it)) }
    }
    @Test fun searchIgnoresAccentsCaseAndSurroundingSpaces() {
        assertEquals(1, listOf(demoRecipe().copy(title = "Pão de queijo")).search(" PAO ").size)
        assertTrue(listOf(demoRecipe()).search("sopa").isEmpty())
    }
    @Test fun sampleDoesNotInventMissingQuantities() {
        val sample = demoRecipe()
        assertEquals("", sample.ingredients.first { it.name == "Fraldinha" }.quantity)
        assertEquals("4 ou 5", sample.ingredients.first { it.name == "Batatas" }.quantity)
    }
}
