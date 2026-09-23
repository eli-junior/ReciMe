# Instruções do Projeto ReciMe

Este projeto usa **Ariad**. O agente é o **Driver**; a pessoa é o **Navigator**.

O ReciMe é um projeto de aprendizado para criar um produto web pessoal com uma ponte Android para importar receitas de Reels públicos do Instagram. O fluxo inicial é: compartilhar o link para o app, encaminhar a URL à API, processar a extração no backend e encontrar na web novas receitas para ajustar, revisar e salvar na coleção.

## Contexto obrigatório

Antes de trabalho relevante, leia os arquivos que existirem nesta ordem:

- `README.md`
- `docs/project/briefing.md`
- `docs/project/decisions/index.md` e os registros pertinentes
- `docs/project/roadmap/index.md` e o item ativo
- `docs/project/debt/index.md` e os itens pertinentes
- `docs/process/development-guide.md`
- `docs/process/worklog/index.md` e entradas recentes
- `docs/product/principles.md`
- `CHANGELOG.md`

`00_BRIEFING.md` é a especificação-fonte extensa. Consulte-o quando precisar de contexto adicional; `docs/project/briefing.md` contém as decisões operacionais consolidadas.

## Direção do produto

- O ReciMe original é referência funcional, não um alvo visual a ser copiado.
- A primeira versão tem interface web e uma ponte Android de compartilhamento e atende inicialmente um único usuário, sem autenticação de produto.
- O app depende do backend; funcionamento offline não faz parte da primeira versão.
- A receita precisa ser revisável na web antes de entrar na coleção: título, ingredientes e etapas são editáveis. Importações e rascunhos são persistidos antes da revisão.
- A extração nunca deve inventar informação. Ausências devem aparecer como `não informado`.
- A importação começa por Reels de contas públicas. Falhas de acesso devem ser explicadas de forma clara.
- A interface e a saída da extração são em português do Brasil; conteúdo estrangeiro deve ser traduzido quando possível.
- A exploração do aplicativo de referência tem prioridade enquanto o Navigator tiver acesso Pro temporário. Peça prints ou esclarecimentos de navegação quando isso reduzir uma incerteza relevante.

## Forma de trabalho

Para trabalho não trivial, conduza o ciclo Ariad: orientar, planejar, implementar, testar e preparar uma rota de validação, revisar, documentar e propor o histórico. Pare nos checkpoints definidos no guia local; uma confirmação só libera a etapa seguinte.

Não amplie o escopo silenciosamente. Registre descobertas que não bloqueiem a entrega como decisão aberta, dívida ou trabalho futuro.

Para mudanças pequenas de documentação, apresente a alteração e sua verificação antes de propor um commit. Não faça commit ou push sem confirmação explícita do Navigator.

O backend será hospedado no miniPC Ubuntu do Navigator, usando Docker, domínio próprio e Cloudflare. Não publique serviços, altere DNS ou acesse a infraestrutura externa sem instrução explícita.
