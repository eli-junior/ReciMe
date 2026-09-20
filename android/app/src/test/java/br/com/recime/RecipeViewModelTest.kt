package br.com.recime

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class RecipeViewModelTest {
    private val dispatcher = StandardTestDispatcher()
    @Before fun setup() { Dispatchers.setMain(dispatcher) }
    @After fun cleanup() { Dispatchers.resetMain() }

    @Test fun cancelledImportCannotOpenReviewLater() = runTest(dispatcher) {
        val model = RecipeViewModel()
        model.openImport()
        model.importDemo()
        runCurrent()
        assertNotNull(model.stage)
        model.back()
        advanceUntilIdle()
        assertEquals(Screen.Library, model.screen)
        assertNull(model.stage)
        assertTrue(model.recipes.isEmpty())
    }

    @Test fun importRequiresReviewAndEditsAreSavedWithoutDuplicating() = runTest(dispatcher) {
        val model = RecipeViewModel()
        model.openImport()
        model.importDemo()
        advanceUntilIdle()
        assertEquals(Screen.Review, model.screen)
        assertTrue(model.recipes.isEmpty())
        model.update(model.draft.copy(title = "Almoço de domingo"))
        model.save()
        assertEquals("Almoço de domingo", model.recipes.single().title)
        model.edit()
        model.update(model.draft.copy(title = "Fraldinha da casa"))
        model.save()
        assertEquals("Fraldinha da casa", model.recipes.single().title)
    }

    @Test fun invalidLinkNeverStartsImport() = runTest(dispatcher) {
        val model = RecipeViewModel()
        model.openImport()
        model.url = "https://example.com"
        model.importDemo()
        advanceUntilIdle()
        assertEquals(Screen.Import, model.screen)
        assertNotNull(model.error)
        assertNull(model.stage)
    }
}
