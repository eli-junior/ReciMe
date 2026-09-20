# ReciMe — prova de extração

Projeto de aprendizado Android. Etapa atual: comprovar URL de Reel público → vídeo/legenda → receita estruturada, antes de escolher backend e banco.

## Executar no Ubuntu WSL

```bash
cd /mnt/d/projetos/ReciMe
uv sync
uv run pytest -q
uv run python probe.py 'https://www.instagram.com/reel/CODIGO/'
```

O comando padrão só tenta adquirir vídeo e metadados: não chama IA. Não usa cookies, login ou configurações pessoais do yt-dlp. Formato experimental: MP4 com áudio e vídeo juntos, até 100 MiB. Se não houver esse formato, registrar falha; não é evidência de que o Reel não existe.

Para extrair, preencha `GEMINI_API_KEY` no `.env` da raiz (já criado localmente). Em um novo clone, copie `.env.example` para `.env`. A configuração é lida pelo `python-decouple`; variáveis do ambiente têm prioridade sobre o arquivo. O `.env` é ignorado pelo Git, e o `.env.example` contém apenas campos vazios.

```bash
uv run python probe.py 'https://www.instagram.com/reel/CODIGO/' --extract
```

`--extract` habilita uma geração paga por execução, sem repetição automática, usando Gemini 2.5 Flash. Não existe controle acumulado de orçamento nesta primeira prova: rodar manualmente, conferir uso no relatório e faturamento antes de repetir. O teto sugerido de US$ 2 ainda deve ser confirmado antes de execução pelo Driver. Não usar em lote sem esse controle.

Resultados ficam em `artifacts/<id>/`: vídeo, metadados, relatório, resposta bruta e receita validada. A pasta inteira é ignorada pelo Git; metadados e erros podem conter URLs temporárias. A fonte é anexada pelo script, não gerada pela IA. Upload remoto é removido ao final quando possível; falha de limpeza é registrada.

Timeout: aquisição limitada a 120s; processamento remoto tem janela de 120s; chamadas HTTP têm timeout de 120s. São limites por etapa/chamada, não um limite global de 120s. Ctrl+C interrompe a prova, sem promessa de cancelar cobrança já iniciada.

## Validar manualmente

1. Executar sem `--extract` para cinco Reels públicos (legenda completa, fala, texto visual, informação ausente e outro idioma).
2. Conferir `report.json`: status acquired e arquivo MP4 reproduzível com áudio significam aquisição bem-sucedida. Erro de login é falha de acesso; não fornecer cookies como solução automática.
3. Com chave e orçamento, executar com `--extract`; comparar `recipe.json` à fonte e aos timestamps. Esperado: pt-BR, nenhuma quantidade inventada, null para ausência, evidências e warnings. JSON válido sozinho não comprova fidelidade.
4. Registrar por caso tempos, tokens, acertos e falhas. Não declarar viabilidade por link se aquisição falhar, mesmo que a IA funcione por outro caminho.

Esta CLI é operada localmente com URLs escolhidas pelo Navigator; não é um endpoint público. Validação de host de entrada não substitui proteção de rede/redirects necessária antes de aceitar URLs de terceiros num servidor.

Não há app, API ou banco implementados. Kotlin + Compose permanece recomendação para etapa posterior. Nutrição foi excluída deliberadamente do primeiro escopo, conforme o briefing consolidado.
