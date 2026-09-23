# Briefing do Projeto

## Propósito

O ReciMe é um projeto de aprendizado para o Navigator aprender desenvolvimento de um produto web com integração Android revisando uma implementação real. O produto transforma Reels públicos do Instagram em receitas estruturadas, para que uma pessoa possa guardar e recuperar receitas que encontrou nas redes sociais.

## Estado atual

Há uma prova Python de aquisição e extração e uma demonstração Android histórica em Kotlin + Jetpack Compose, testada anteriormente pelo Navigator. A aquisição de um Reel real foi validada; a geração Gemini falhou com `ClientError` e foi adiada. O plano DS3 aprovado antecipou uma API FastAPI, banco SQLite, executor separado e interface web com Jinja2, CSS e JavaScript. A implementação web usa extração simulada, passou pelos testes automatizados locais no Windows e aguarda validação manual. A ponte Android e a extração real integrada permanecem pendentes.

## Primeira entrega

Uma pessoa no Android compartilha a URL de um Reel público para o ReciMe. O aplicativo apenas encaminha a URL à API e informa aceitação ou falha do envio. O backend registra a importação e processa a extração sem depender de o app ou a web estarem abertos. Ao acessar a web, a pessoa encontra novas receitas pendentes para ajustar. Importações e rascunhos são persistidos antes da revisão; somente receitas confirmadas entram na coleção. O backend usa serviços de IA em nuvem para interpretar legenda, fala e conteúdo visual; na web, a pessoa revisa e pode editar o título, os ingredientes e as etapas antes de salvar. Depois, encontra receitas salvas na web em uma lista com imagem, título e busca por nome.

A web e a ponte Android usam português do Brasil. Conteúdo de origem em outro idioma deve ser traduzido quando possível. Informações não presentes na fonte devem permanecer como `não informado`; a IA não deve completar lacunas com estimativas.

## Premissas de arquitetura

- A interface principal é web. Para a etapa local, foi aprovado FastAPI/Pydantic, Jinja2 com CSS e JavaScript, SQLite e executor separado com fila persistida. O Android receberá o compartilhamento e enviará a URL à API; o reaproveitamento da demonstração Kotlin + Jetpack Compose será avaliado em plano próprio.
- O backend e o banco serão hospedados no miniPC Ubuntu do Navigator, com Docker, domínio próprio e Cloudflare.
- A primeira versão depende de conexão com o backend e será usada inicialmente só pelo Navigator, sem autenticação de produto.
- A extração usa APIs de IA, sem modelos locais.
- A viabilidade de obter e analisar vídeos públicos do Instagram, o provedor de IA, custo e tempo de resposta precisam ser validados antes de se tornarem compromissos de arquitetura.

## Premissas de produto

- O ReciMe original inspira o fluxo, mas o ReciMe terá identidade visual própria.
- A revisão na web é obrigatória antes de incluir uma receita na coleção; importações e rascunhos são persistidos previamente.
- A ponte Android deve explicar falhas de envio. A web deve distinguir importações em processamento, prontas para revisão e com falha, oferecendo nova tentativa ou descarte quando pertinente.
- O primeiro escopo não inclui nutrição, livros de receitas, lista de compras, plano de refeições, modo cozinha, compartilhamento público ou assistente culinário.

## Restrições

- Aceitar inicialmente apenas Reels de contas públicas; não depender do login do Instagram do usuário.
- Não prometer extração em 15 segundos antes de medir vídeos reais. O envio pelo Android não exige aguardar a extração; andamento e resultado ficam disponíveis na web.
- Preservar atribuição e URL da fonte quando disponíveis.
- Não enviar dados ou publicar infraestrutura sem autorização explícita do Navigator.
- Definir um teto de gastos antes de testes pagos recorrentes de IA.

## Notas operacionais

O Driver implementa e explica decisões de código; o Navigator aprende revisando e valida manualmente as entregas. O Navigator tem acesso Pro temporário ao aplicativo de referência e pode fornecer prints ou esclarecer fluxos enquanto esse acesso existir.

## Glossário

- **Reel público:** vídeo do Instagram disponível sem autenticação e elegível para importação inicial.
- **Extração:** transformação de legenda, áudio e imagens do Reel em campos estruturados de receita.
- **Revisão:** etapa anterior ao salvamento em que a receita extraída pode ser corrigida.
- **Fonte:** URL, autoria e mídia de origem preservadas para referência e atribuição.
