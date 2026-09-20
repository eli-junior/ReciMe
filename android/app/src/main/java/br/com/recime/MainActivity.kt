package br.com.recime

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent { ReciMeApp() }
    }
}

private val Cream = Color(0xFFFAF7F0)
private val Green = Color(0xFF315B45)

@Composable
fun ReciMeApp(model: RecipeViewModel = viewModel()) {
    MaterialTheme(colorScheme = lightColorScheme(
        primary = Green, background = Cream, surface = Cream,
        secondaryContainer = Color(0xFFE8EDDF), onSecondaryContainer = Color(0xFF263C2D),
        surfaceVariant = Color(0xFFF0EADD), onSurface = Color(0xFF252C26),
    )) {
        BackHandler(enabled = model.screen != Screen.Library) { model.back() }
        Scaffold(containerColor = Cream) { padding ->
            Column(Modifier.fillMaxSize().padding(padding).imePadding()) {
                Row(Modifier.fillMaxWidth().padding(horizontal = 24.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically) {
                    Text("reciMe", fontFamily = FontFamily.Serif, fontWeight = FontWeight.Bold,
                        fontSize = 30.sp, color = Green, modifier = Modifier.weight(1f))
                    Surface(color = MaterialTheme.colorScheme.secondaryContainer, shape = RoundedCornerShape(30.dp)) {
                        Text("DEMONSTRAÇÃO", fontSize = 10.sp, letterSpacing = 1.sp,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp))
                    }
                }
                if (model.screen != Screen.Library) {
                    TextButton(onClick = model::back, modifier = Modifier.padding(start = 12.dp)) {
                        Text(if (model.stage != null) "Cancelar importação" else "← Minhas receitas")
                    }
                }
                when (model.screen) {
                    Screen.Library -> Library(model)
                    Screen.Import -> Import(model)
                    Screen.Review -> Review(model)
                    Screen.Detail -> Detail(model)
                }
            }
        }
    }
}

@Composable
private fun Heading(eyebrow: String, title: String, description: String) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Text(eyebrow.uppercase(), color = Green, fontSize = 11.sp, letterSpacing = 2.sp)
        Text(title, fontFamily = FontFamily.Serif, fontSize = 34.sp, lineHeight = 39.sp)
        Text(description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

@Composable
private fun Library(model: RecipeViewModel) {
    val results = model.recipes.search(model.query)
    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)) {
        item { Heading("Seu caderno de cozinha", "Boas receitas\nficam por aqui.", "Guarde as ideias que dão vontade de ir para a cozinha.") }
        item { Button(onClick = model::openImport, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text("+ Importar receita") } }
        item { OutlinedTextField(value = model.query, onValueChange = { model.query = it },
            label = { Text("Buscar por nome") }, singleLine = true, modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) }
        item { Text("MINHAS RECEITAS · ${model.recipes.size}", fontSize = 11.sp, letterSpacing = 1.sp, color = Green) }
        if (results.isEmpty()) item {
            Surface(shape = RoundedCornerShape(24.dp), color = MaterialTheme.colorScheme.secondaryContainer) {
                Column(Modifier.fillMaxWidth().padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(if (model.recipes.isEmpty()) "Seu caderno começa com uma receita." else "Nenhuma receita encontrada.",
                        fontFamily = FontFamily.Serif, fontSize = 24.sp)
                    Text(if (model.recipes.isEmpty()) "Experimente importar a fraldinha com crosta de alho. Você poderá revisar tudo antes de salvar." else "Tente outra palavra do título.")
                }
            }
        }
        items(results, key = { it.id }) { recipe ->
            Card(onClick = { model.open(recipe) }, shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = Color.White)) {
                Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("RECEITA DE EXEMPLO", fontSize = 10.sp, color = Green, letterSpacing = 1.sp)
                    Text(recipe.title, fontFamily = FontFamily.Serif, fontSize = 25.sp)
                    Text("${recipe.ingredients.size} ingredientes · Ver receita →", style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        item { Text("Nesta demonstração, as receitas ficam disponíveis durante a sessão. Fechar o processo do app apaga os dados.", style = MaterialTheme.typography.bodySmall) }
    }
}

@Composable
private fun Import(model: RecipeViewModel) {
    val stages = listOf("Recebendo o link", "Preparando o exemplo", "Organizando a receita")
    LazyColumn(contentPadding = PaddingValues(24.dp), verticalArrangement = Arrangement.spacedBy(24.dp)) {
        item { Heading("Da inspiração ao prato", "Uma nova ideia\npara cozinhar.", "Cole um link do Instagram para experimentar o fluxo.") }
        item { Notice("Importação simulada: qualquer link válido abre a mesma receita de fraldinha. Nenhum vídeo será baixado ou enviado à IA.") }
        item { OutlinedTextField(value = model.url, onValueChange = { model.url = it },
            label = { Text("Link do Instagram") }, enabled = model.stage == null,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
            modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) }
        model.error?.let { message -> item { Text(message, color = MaterialTheme.colorScheme.error) } }
        if (model.stage == null) item {
            Button(onClick = model::importDemo, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text("Experimentar importação") }
        } else {
            item { LinearProgressIndicator(modifier = Modifier.fillMaxWidth()) }
            items(stages.indices.toList()) { index ->
                Text("${index + 1}. ${stages[index]}", color = if (index == model.stage) Green else MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = if (index == model.stage) FontWeight.Bold else FontWeight.Normal)
            }
            item { Text("Simulação em andamento. Você pode cancelar a qualquer momento.") }
        }
    }
}

@Composable
private fun Notice(text: String) {
    Surface(color = MaterialTheme.colorScheme.secondaryContainer, shape = RoundedCornerShape(16.dp)) {
        Text(text, Modifier.fillMaxWidth().padding(16.dp), style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun Review(model: RecipeViewModel) {
    val recipe = model.draft
    LazyColumn(contentPadding = PaddingValues(24.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        item { Heading("Um toque seu", "Revise antes\nde guardar.", "Confira o título, os ingredientes e cada etapa. Tudo aqui pode ser editado.") }
        item { Notice("Exemplo transcrito da legenda, sem extração por IA. Campos vazios significam “não informado”; você não precisa inventar quantidades.") }
        item { OutlinedTextField(recipe.title, { model.update(recipe.copy(title = it)) },
            label = { Text("Título da receita") }, modifier = Modifier.fillMaxWidth()) }
        item { Text("Ingredientes", fontFamily = FontFamily.Serif, fontSize = 26.sp) }
        items(recipe.ingredients.indices.toList()) { index ->
            val ingredient = recipe.ingredients[index]
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(ingredient.name, { name -> model.update(recipe.copy(ingredients = recipe.ingredients.mapIndexed { i, v -> if (i == index) v.copy(name = name) else v })) },
                    label = { Text("Ingrediente ${index + 1}") }, placeholder = { Text("não informado") }, modifier = Modifier.fillMaxWidth())
                OutlinedTextField(ingredient.quantity, { quantity -> model.update(recipe.copy(ingredients = recipe.ingredients.mapIndexed { i, v -> if (i == index) v.copy(quantity = quantity) else v })) },
                    label = { Text("Quantidade · ingrediente ${index + 1}") }, placeholder = { Text("não informado") }, modifier = Modifier.fillMaxWidth())
                TextButton(onClick = { model.update(recipe.copy(ingredients = recipe.ingredients.filterIndexed { i, _ -> i != index })) }) { Text("Remover ingrediente ${index + 1}") }
            }
        }
        item { OutlinedButton(onClick = { model.update(recipe.copy(ingredients = recipe.ingredients + Ingredient(""))) }) { Text("+ Adicionar ingrediente") } }
        item { Text("Modo de preparo", fontFamily = FontFamily.Serif, fontSize = 26.sp) }
        items(recipe.steps.indices.toList()) { index ->
            Column {
                OutlinedTextField(recipe.steps[index], { text -> model.update(recipe.copy(steps = recipe.steps.mapIndexed { i, v -> if (i == index) text else v })) },
                    label = { Text("Etapa ${index + 1}") }, placeholder = { Text("não informado") }, modifier = Modifier.fillMaxWidth())
                TextButton(onClick = { model.update(recipe.copy(steps = recipe.steps.filterIndexed { i, _ -> i != index })) }) { Text("Remover etapa ${index + 1}") }
            }
        }
        item { OutlinedButton(onClick = { model.update(recipe.copy(steps = recipe.steps + "")) }) { Text("+ Adicionar etapa") } }
        model.error?.let { message -> item { Text(message, color = MaterialTheme.colorScheme.error) } }
        item { Button(onClick = model::save, modifier = Modifier.fillMaxWidth().heightIn(min = 52.dp)) { Text("Salvar na sessão") } }
    }
}

@Composable
private fun Detail(model: RecipeViewModel) {
    val recipe = model.draft
    LazyColumn(contentPadding = PaddingValues(24.dp), verticalArrangement = Arrangement.spacedBy(18.dp)) {
        item { Heading("Guardada nesta sessão", recipe.title, "Receita de exemplo · fonte: Guilherme Araujo (@gui.tank)") }
        item { OutlinedButton(onClick = model::edit) { Text("Editar receita") } }
        item { Text("Ingredientes", fontFamily = FontFamily.Serif, fontSize = 26.sp) }
        if (recipe.ingredients.isEmpty()) item { Text("não informado") }
        items(recipe.ingredients) { ingredient ->
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(ingredient.name.ifBlank { "não informado" }, modifier = Modifier.weight(1f))
                Text(ingredient.quantity.ifBlank { "não informado" }, modifier = Modifier.weight(1f), color = Green)
            }
            HorizontalDivider(Modifier.padding(top = 12.dp))
        }
        item { Text("Modo de preparo", fontFamily = FontFamily.Serif, fontSize = 26.sp) }
        if (recipe.steps.isEmpty()) item { Text("não informado") }
        items(recipe.steps.indices.toList()) { index ->
            Text("${index + 1}. ${recipe.steps[index].ifBlank { "não informado" }}", lineHeight = 25.sp)
        }
        item { Text("Fonte original\n${recipe.source}", style = MaterialTheme.typography.bodySmall) }
    }
}
