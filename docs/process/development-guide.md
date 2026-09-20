# Guia de Desenvolvimento Local

Este é o contrato operacional do ReciMe. Ele adapta Ariad ao projeto; em caso de conflito, este guia prevalece e a diferença deve ser registrada na checagem de coerência.

## Ambiente atual

Ambiente de desenvolvimento autorizado: Ubuntu-26.04 no WSL. A prova local está em `probe.py`; instalar com `uv sync`, verificar com `uv run pytest -q` e consultar comandos e limites no `README.md`. Banco, backend e app ficam para depois da prova de aquisição e extração. O lockfile fixa as dependências Python da prova.

Além da prova Python, há uma demonstração Android em `android/`, com Kotlin + Compose e dados em memória. Backend e banco continuam pendentes. Compilação, testes e roteiro manual estão em `android/README.md`. A branch principal é `main`. O Navigator autorizou a publicação inicial como repositório público `eli-junior/ReciMe`. O `.env`, ambientes virtuais, builds Android e resultados em `artifacts/` ficam fora do histórico; `.env.example` contém apenas campos vazios.

O destino de produção planejado é um miniPC Ubuntu do Navigator, com Docker, domínio próprio e Cloudflare. Mudanças nessa infraestrutura, em DNS e em serviços externos exigem orientação explícita do Navigator.

## Entrega e validação

Para histórias não triviais, siga o ciclo Ariad e pare para confirmação do Navigator:

1. **Plano:** apresente escopo, aceitação, decisões, exclusões, versão pretendida e riscos antes de alterar código de implementação.
2. **Validação:** após os testes automatizados, entregue uma rota manual com comandos, URL ou tela, dados de exemplo, observação esperada, condição de aprovação e condição de falha.
3. **Revisão:** apresente avaliação de refatoração, dívida técnica e documentação pendente antes de atualizar os registros de encerramento.
4. **Histórico:** proponha o commit somente após a aceitação da documentação. Não há push sem confirmação explícita.

Em mudanças pequenas de documentação ou configuração, use o ciclo comprimido: explique a alteração, verifique os arquivos e aguarde confirmação antes de propor o histórico.

## Documentação e memória

- Atualize `docs/project/briefing.md` quando uma premissa estável mudar.
- Crie uma decisão em `docs/project/decisions/records/` para escolhas que evitam rediscussão ou rework.
- Cada item de roadmap mantém seu próprio estado; o índice não é uma tabela de acompanhamento.
- Registre dívida que sobreviverá à história em `docs/project/debt/items/`.
- Registre um marco concluído em um arquivo novo de `docs/process/worklog/entries/`.
- Atualize o changelog apenas ao fechar uma versão, com evidência Git. Não use uma seção `Unreleased`.

## Regras específicas do produto

- Trate extração de vídeo, tempo de resposta e custo como hipóteses até testadas com Reels públicos reais.
- Antes de testes pagos recorrentes, proponha limite de gasto e evidência a coletar.
- Dados ausentes da fonte devem permanecer como `não informado`; não use inferência para preencher lacunas como fato.
- Preserve autoria e URL da fonte quando disponíveis.
- Para mudanças de fluxo ou interface inspiradas no app de referência, peça ao Navigator prints ou esclarecimentos enquanto o acesso Pro estiver ativo se isso resolver uma ambiguidade material.

## Política de histórico

Inicialize Git antes da primeira implementação, caso o Navigator mantenha esta pasta como repositório do projeto. Faça commits pequenos e coerentes após validação e aceitação. Use mensagens em português que expliquem a intenção da mudança. O primeiro versionamento será definido ao fechar uma entrega funcional, não durante o bootstrap documental.
