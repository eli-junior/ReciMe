# Especificação Técnica e Funcional: Clone ReciMe (Engenharia de Software e Produto)

Este documento estabelece os requisitos técnicos, arquiteturais, funcionais, de design (UI/UX) e regras de negócio para a implementação de um clone do aplicativo **ReciMe**, baseado no fluxo completo demonstrado no vídeo de referência (captura de Reels/Instagram, extração com IA, gestão nutricional, categorização em livros de receitas e modo interativo).

---

## 1. Visão Geral do Produto

O aplicativo tem como proposta de valor ser o organizador definitivo de receitas digitais do usuário. Ele permite importar instantaneamente receitas em vídeo (Instagram Reels, TikTok, YouTube Shorts) ou páginas web através da folha de compartilhamento nativa do sistema operacional, estruturando automaticamente texto, ingredientes, quantidades, passos numerados e cálculo nutricional com Inteligência Artificial.

---

## 2. Arquitetura de Alto Nível e Stack Tecnológica

### 2.1 Front-end Mobile
* **Framework:** React Native (com Expo bare workflow) ou Flutter.
* **Gerenciamento de Estado:** Zustand / Redux Toolkit (React Native) ou Riverpod / Bloc (Flutter).
* **Deep Linking & Intent Filters:** Configuração no `AndroidManifest.xml` e `Info.plist` para interceptar `text/plain` e URLs via Share Sheet.
* **Componentes Gráficos e Ícones:** Lucide Icons / Phosphor Icons + SVGs customizados para ingredientes e ilustrações orgânicas.

### 2.2 Back-end & Ingestion Engine
* **API Gateway & Core API:** FastAPI (Python) ou Node.js / NestJS.
* **Pipeline de Extração de Receitas:**
  1. **Crawler/Scraper:** Download dos metadados e legenda do post/vídeo (via APIs oficiais ou scrapers headless assíncronos como `yt-dlp` / Puppeteer).
  2. **Áudio Transcription (Fallback):** Whisper API para transcrever a fala do criador caso a legenda seja insuficiente.
  3. **LLM Parser (Extração Estruturada):** Integração com modelos (GPT-4o Mini, Claude 3.5 Haiku ou Gemini 1.5 Flash) via JSON Schema / Function Calling para extrair:
     * Título
     * Rendimento (porções originais)
     * Tempo de preparo / cocção
     * Lista de ingredientes normalizados (nome, quantidade numérica, unidade de medida, grupo/crosta)
     * Instruções passo a passo ordenadas
     * Imagem de capa (thumbnail) e link da fonte original
* **Módulo Nutricional:**
  * Estimador de calorias e macronutrientes (Proteínas, Carboidratos, Gorduras) baseado na lista normalizada de ingredientes cruzada com tabela TACO/USDA ou inferência assistida por LLM com fórmula ponderada.
* **Banco de Dados:**
  * PostgreSQL com extensão `pgvector` (para buscas semânticas e assistente virtual).
  * Redis para cache de extrações idênticas e rate-limiting.
* **Storage de Mídia:** AWS S3 / Cloudflare R2 para fotos enviadas pelo usuário e thumbnails armazenadas em cache.
* **Autenticação:** Google Sign-In nativo (Android Credential Manager / OAuth 2.0), Apple Sign-In e Email Magic Link.

---

## 3. Especificação Funcional por Módulos

### Módulo 1: Interceptação e Compartilhamento Externo (Share Intent)
* **Entrada:** Link de post de rede social (ex: Instagram Reel) enviado pelo menu "Compartilhar" nativo do Android/iOS.
* **Comportamento:**
  1. O aplicativo é aberto diretamente na tela modal de processamento (`Importando...`).
  2. Um botão "Cancelar" permite ao usuário abortar a operação e voltar à tela inicial.
  3. A extração ocorre de forma assíncrona com timeout estrito de 15 segundos.
  4. Ao finalizar, transiciona suavemente para a tela de **Preview da Receita Importada**.

### Módulo 2: Preview da Receita e Edição Rápida
* **Cabeçalho:**
  * Thumbnail circular/arredondada da receita.
  * Título extraído com capacidade de truncamento elíptico.
  * Botão de atalho rápido "Editar receita" (leva para o Módulo 5).
* **Ingredientes:**
  * Renderização com agrupamentos/seções (ex: "Para a crosta de alho crocante:").
  * Mapeamento semântico automático de ícones correspondentes a cada item (ex: alho, queijo, manteiga, azeite, carne, temperos).
* **Instruções:**
  * Lista sequencial numerada com destaque em termos técnicos ou de tempo (ex: "220°C por 45 minutos").
* **Nutrição e Porções:**
  * Exibição do resumo nutricional por porção.
  * Botão interativo **"Calcular nutrição"**:
    - Abre Bottom Sheet para confirmar a quantidade de porções (stepper numérico: `-` e `+`).
    - Recalcula dinamicamente os valores de calorias totais e macronutrientes (Proteínas, Carboidratos, Gorduras).
    - Exibe gráfico Donut Chart SVG estilizado com as cores dos nutrientes.
* **Rodapé Fixo (Sticky Action Bar):**
  * Seletor de Livro de Receitas ("Livro de receitas > [Categoria]").
  * Botão primário full-width **"Salvar"**.
  * Link discreto "Reportar erro" para feedbacks de falha na extração.

### Módulo 3: Organização em Livros de Receitas (Collections)
* **Fluxo de Seleção:**
  * Bottom sheet modal que lista coleções existentes com checkbox ativo na coleção atual.
  * Botão de topo: `+ Novo livro de receitas`.
* **Criação Rápida:**
  * Campo de texto com placeholder contextual ("por exemplo, jantar durante a semana").
  * Contador de caracteres (limite: 50 caracteres).
  * O botão "Criar livro de receitas" só se torna clicável quando o input é válido (> 0 caracteres).
  * Ao criar, a nova pasta é imediatamente selecionada e o modal se fecha.

### Módulo 4: Autenticação Progressiva (Just-in-Time Auth)
* **Regra de Negócio:** O usuário pode importar e visualizar a receita como visitante (Guest Mode). A exigência de login só ocorre no momento do clique em **"Salvar"** (se não autenticado previamente).
* **Fluxo:**
  1. Bottom sheet / tela cheia de criação de conta com destaque para "Continuar com Google".
  2. Conclusão do fluxo com tela de celebração ("Conta criada! 🎉 Faça login em qualquer dispositivo para acessar suas receitas de qualquer lugar.").
  3. Persistência imediata da receita em rascunho vinculada ao recém-criado `user_id`.

### Módulo 5: Editor Detalhado de Receitas
* **Campos Editáveis:**
  * Nome da receita.
  * Foto principal (opção de tirar foto ou buscar da galeria local).
  * Metadados: Porções, Nutrição detalhada, Etiquetas (Tags temáticas).
  * Lista de Ingredientes:
    - Adicionar novo item / cabeçalho de seção.
    - Modo de reordenação (drag and drop).
    - Botão de exclusão pontual (ícone de lixeira / 'x' vermelho).
  * Lista de Instruções:
    - Adicionar novo passo ou título de etapa (comutador de tipo: "Título" vs "Normal").
    - Adicionar imagem individual por passo de instrução.
    - Modo de reordenação.

### Módulo 6: Tela de Detalhes da Receita (View Mode)
* **Hero Header:** Foto expandida com botões flutuantes: Voltar (`<`), Editar, Menu Contextual (`...`) e Foto (`📷`).
* **Tags e Ações Rápidas:**
  * Tag clicável do livro de receitas associado.
  * Barra de botões de ação em pílula com ícones circulares:
    * **Plano:** Agenda a receita no Meal Planner semanal.
    * **Lista:** Adiciona todos os ingredientes (ou faltantes) à Lista de Compras.
    * **Fixar:** Fixa no topo da tela inicial.
    * **Compartilhar:** Gera link público ou imagem/PDF para envio externo.
* **Atribuição de Fonte:** Banner com avatar e @ do criador original ("Receita de gui.tank") + link direto "Abrir Instagram".
* **Controle de Execução e Gamificação:**
  * Toggle Switch: "Marcar como cozinhado".
  * Avaliação por estrelas interativas (1 a 5 estrelas).
  * Campo para notas pessoais e ajustes de cozinha.
* **Cálculo de Proporção Interativo:**
  * Stepper `- [X] porções +` que recalcula dinamicamente em tempo de tela as quantidades dos ingredientes multiplicando pelo fator `porções_atuais / porções_base`.
  * Botão de conversão de unidades (Métrico x Imperial).
* **Modo Cozinha (Cook Mode):**
  * Botão "Cozinhe passo a passo": abre interface em tela cheia com fonte ampliada, timer integrado e wake-lock para a tela não apagar durante o cozimento.
* **Assistente Culinário IA ("Pergunte ao ReciMe"):**
  * Botão flutuante estilizado.
  * Prompts pré-configurados em chips:
    * `Substituir ingrediente`: sugere trocas para alérgenos ou itens ausentes na despensa.
    * `Deixe mais fácil`: simplifica etapas demoradas.
    * `Deixe mais saudável`: reduz teor de gordura/sódio sem perder a estrutura do prato.
  * Campo de chat livre para tirar dúvidas em tempo real ("Posso fazer na Airfryer?").

---

## 4. Guia de Estilo, UI e Design System

### 4.1 Paleta de Cores
| Elemento | Hexadecimal | Descrição |
| :--- | :--- | :--- |
| **Primary Brand Blue** | `#2979FF` | Utilizado no logotipo, FAB principal e botões de destaque |
| **Primary Action Black** | `#1A1A1A` | Cor predominante de botões de confirmação ("Salvar", "Continuar") |
| **Background Neutro** | `#FFFFFF` / `#F8F9FA` | Fundo limpo para garantir legibilidade de receitas |
| **Card / Surface Light** | `#F3F4F6` | Fundo de badges, chips e inputs |
| **Nutrição - Proteína** | `#F06292` | Rosa suave para proteínas |
| **Nutrição - Carboidrato** | `#FBC02D` | Amarelo dourado para carboidratos |
| **Nutrição - Gordura** | `#4CAF50` | Verde folha para lipídios/gorduras |
| **Cores Brand Acentos** | `#E57373`, `#81C784`, `#FFD54F`, `#BA68C8` | Formas orgânicas da logo e loaders |

### 4.2 Tipografia e Componentes
* **Família Tipográfica:** Inter, SF Pro Rounded ou Plus Jakarta Sans (arredondada, moderna e amigável).
* **Hierarquia:**
  * Títulos: 20–24pt Semi-bold / Bold.
  * Subtítulos de Seção: 16–18pt Bold (Caps lock sutil em cabeçalhos de grupos).
  * Texto de Corpo e Passos: 14–15pt Regular com line-height relaxado (1.5).
* **Bordas e Sombras:**
  * Border Radius generoso em modais e botões (`rounded-2xl`: 16px a 24px).
  * Botões de ação primária tipo cápsula/pílula (`rounded-full`).

---

## 5. Modelo de Dados (Entidades Principais)

### 5.1 Diagrama Entidade-Relacionamento Lógico

```
User (1) ────< Recipe (N)
User (1) ────< RecipeBook (N)
Recipe (N) ───< RecipeBookRecipe >─── (M) RecipeBook
Recipe (1) ───< RecipeIngredient (N)
Recipe (1) ───< RecipeStep (N)
Recipe (1) ───< RecipeNutrition (1)
Recipe (1) ───< UserCookingLog (N)
```

### 5.2 Estrutura das Tabelas (PostgreSQL / SQL Model)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recipe_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(50) NOT NULL,
    is_private BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recipes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) DEFAULT 'instagram', -- 'instagram', 'tiktok', 'manual', 'web'
    source_url TEXT,
    author_name VARCHAR(100),
    cover_image_url TEXT,
    servings INTEGER DEFAULT 4,
    prep_time_minutes INTEGER,
    cook_time_minutes INTEGER,
    is_pinned BOOLEAN DEFAULT FALSE,
    cooked_count INTEGER DEFAULT 0,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    personal_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE recipe_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    section_title VARCHAR(100), -- ex: 'Para a crosta' ou NULL
    raw_text TEXT NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    amount NUMERIC(8,2),
    unit VARCHAR(50),
    icon_slug VARCHAR(50), -- ex: 'garlic', 'beef', 'oil'
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE recipe_steps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    title VARCHAR(150), -- Para passos com cabeçalho
    instruction TEXT NOT NULL,
    image_url TEXT,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE recipe_nutritions (
    recipe_id UUID PRIMARY KEY REFERENCES recipes(id) ON DELETE CASCADE,
    calories NUMERIC(8,2) NOT NULL,
    protein_g NUMERIC(8,2) NOT NULL,
    carbs_g NUMERIC(8,2) NOT NULL,
    fats_g NUMERIC(8,2) NOT NULL,
    calculated_for_servings INTEGER NOT NULL
);
```

---

## 6. Regras de Negócio e Casos de Borda Críticos

1. **Idempotência de Extração:** Se o mesmo usuário compartilhar a mesma URL em um intervalo menor que 2 minutos, o app deve redirecionar diretamente para o rascunho existente em vez de acionar a pipeline de IA novamente.
2. **Normalização Fracionária de Ingredientes:** O parser deve lidar com medidas fracionárias culinárias (ex: "1/2 colher", "uma pitada", "4 a 5 unidades"), armazenando a quantidade nominal e a representação amigável para exibição.
3. **Escalonamento Dinâmico de Porções:**
   * A fórmula para reescalonar a quantidade de um ingrediente é:
     $$Q_{ajustada} = Q_{original} \times \left(\frac{\text{novas\_porções}}{\text{porções\_originais}}\right)$$
   * Se o ingrediente não possuir quantidade explícita (ex: "sal a gosto"), a string permanece inalterada.
4. **Fallback de IA e Redes Protegidas:** Caso a API do Instagram limite a leitura da legenda (ex: conta privada), o sistema deve retornar erro claro: *"Esta conta é privada ou o vídeo não pôde ser lido. Você pode colar a receita manualmente."*
5. **Privacidade e Conformidade:** Os dados extraídos do criador original (avatar e @) devem ser preservados para dar o devido crédito e evitar infração de direitos autorais de conteúdo culinário.