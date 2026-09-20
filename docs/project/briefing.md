# Briefing do Projeto

## Propósito

O ReciMe é um projeto de aprendizado para o Navigator aprender desenvolvimento de aplicativos móveis revisando uma implementação real. O produto transforma Reels públicos do Instagram em receitas estruturadas, para que uma pessoa possa guardar e recuperar receitas que encontrou nas redes sociais.

## Estado atual

Há uma prova Python de aquisição e extração e uma demonstração Android em Kotlin + Jetpack Compose. A aquisição de um Reel real foi validada; a geração Gemini falhou com `ClientError` e foi adiada pelo Navigator. A interface com importação simulada, revisão, salvamento na sessão e busca foi testada pelo Navigator, que optou por mantê-la como está. Ainda não há backend ou banco, nem importação real integrada ao app.

## Primeira entrega

Uma pessoa no Android compartilha a URL de um Reel público para o ReciMe. O aplicativo aguarda a extração, exibindo progresso e permitindo cancelar. O backend usa serviços de IA em nuvem para interpretar legenda, fala e conteúdo visual; a pessoa revisa e pode editar o título, os ingredientes e as etapas antes de salvar. Depois, encontra receitas salvas em uma lista com imagem, título e busca por nome.

O app usa português do Brasil. Conteúdo de origem em outro idioma deve ser traduzido quando possível. Informações não presentes na fonte devem permanecer como `não informado`; a IA não deve completar lacunas com estimativas.

## Premissas de arquitetura

- O cliente inicial usa Kotlin + Jetpack Compose, escolha aprovada pelo Navigator para a demonstração Android. Dados em memória são uma limitação da demonstração; o produto continua dependente do backend.
- O backend e o banco serão hospedados no miniPC Ubuntu do Navigator, com Docker, domínio próprio e Cloudflare.
- A primeira versão depende de conexão com o backend e será usada inicialmente só pelo Navigator, sem autenticação de produto.
- A extração usa APIs de IA, sem modelos locais.
- A viabilidade de obter e analisar vídeos públicos do Instagram, o provedor de IA, custo e tempo de resposta precisam ser validados antes de se tornarem compromissos de arquitetura.

## Premissas de produto

- O ReciMe original inspira o fluxo, mas o ReciMe terá identidade visual própria.
- A tela de revisão é obrigatória antes de persistir uma receita.
- O app deve apresentar falhas de importação de maneira clara e oferecer nova tentativa ou descarte.
- O primeiro escopo não inclui nutrição, livros de receitas, lista de compras, plano de refeições, modo cozinha, compartilhamento público ou assistente culinário.

## Restrições

- Aceitar inicialmente apenas Reels de contas públicas; não depender do login do Instagram do usuário.
- Não prometer extração em 15 segundos antes de medir vídeos reais. O app permanece na tela de importação enquanto a operação estiver ativa.
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
