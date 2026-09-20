package br.com.recime

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

enum class Screen { Library, Import, Review, Detail }

class RecipeViewModel : ViewModel() {
    var screen by mutableStateOf(Screen.Library)
        private set
    var recipes by mutableStateOf(listOf<Recipe>())
        private set
    var draft by mutableStateOf(demoRecipe())
        private set
    var query by mutableStateOf("")
    var url by mutableStateOf(DEMO_URL)
    var error by mutableStateOf<String?>(null)
        private set
    var stage by mutableStateOf<Int?>(null)
        private set
    private var job: Job? = null
    private var nextId = 1L

    fun openImport() { error = null; screen = Screen.Import }
    fun importDemo() {
        if (stage != null) return
        if (!validInstagramUrl(url)) {
            error = "Use um link HTTPS do Instagram com /reel/ ou /p/."
            return
        }
        error = null
        stage = 0
        job = viewModelScope.launch {
            for (step in 0..2) { stage = step; delay(850) }
            // Qualquer URL válida apenas demonstra o fluxo, sem acesso à rede.
            draft = demoRecipe()
            stage = null
            screen = Screen.Review
        }
    }
    fun back() {
        job?.cancel(); job = null; stage = null; error = null
        screen = Screen.Library
    }
    fun update(value: Recipe) { draft = value }
    fun save() {
        if (draft.title.isBlank()) { error = "Informe um título para encontrar sua receita depois."; return }
        val saved = draft.copy(id = if (draft.id == 0L) nextId++ else draft.id, title = draft.title.trim())
        recipes = recipes.filterNot { it.id == saved.id } + saved
        draft = saved
        query = ""
        error = null
        screen = Screen.Detail
    }
    fun open(recipe: Recipe) { draft = recipe; screen = Screen.Detail }
    fun edit() { error = null; screen = Screen.Review }
}
