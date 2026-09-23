---
code: CV1.DS3
level: Delivery Story
status: Validated
status_reason: Navigator informou tudo funcionando; testes automatizados e rota local concluídos
updated: 2026-09-22
---

# API e caixa de entrada web com persistência

## Aprovação e ambiente

O Navigator aprovou este plano e depois orientou executar diretamente com `uv` local no Windows, sem WSL. O executor usa bloqueio de arquivo compatível com Windows e Linux. Rota executável e limitações estão no [roteiro de validação](test-guide.md). Após testar, o Navigator informou “tudo funcionando”. A validação foi aceita.

O relato não discrimina os cenários executados. Não se atribui validação manual individual a reinício, falhas, duas abas, acessibilidade ou larguras específicas de tela. A evidência automatizada já registrada permanece: 37 testes passaram no Windows, sintaxe JavaScript verificada e páginas principais responderam HTTP 200.

## Intenção

Validar o percurso receber uma URL, encontrar uma nova receita na web, ajustar e guardar na biblioteca. A persistência será real; a extração desta etapa será simulada e identificada como demonstração. Não comprova importação real do Instagram nem encerra CV1.

## Escopo proposto

- API para registrar uma URL e devolver o identificador somente após persistir a importação.
- Caixa de entrada web responsiva em pt-BR, com contagem de receitas prontas para ajustar e estados de fila, processamento e falha.
- Revisão de título, ingredientes e etapas, com fonte, avisos e ausências apresentados como `não informado`.
- Ação explícita de salvar na biblioteca; rascunhos ficam separados das receitas confirmadas.
- Biblioteca com detalhe e busca por título; dados preservados após reiniciar o serviço.
- Descarte de pendências e nova tentativa manual de falhas.
- Executor separado da requisição HTTP, consultando tarefas persistidas. Fechar o navegador não interrompe a tarefa.
- Modo de demonstração explícito, com amostra já transcrita no projeto e cenários determinísticos de sucesso e falha, sem downloads nem chamadas de IA. URLs arbitrárias não podem receber a amostra como se fosse sua extração.

## Decisões propostas

Python + FastAPI e Pydantic aproveitam a prova existente. Páginas renderizadas com Jinja2, CSS responsivo e JavaScript pequeno para atualização de estados e edição de listas mantêm API e web no mesmo serviço. SQLite em disco local, com transações e evolução de schema, atende ao recorte de um usuário e um executor; reavaliar PostgreSQL se houver concorrência ou distribuição que justifique a mudança.

O executor usa a fila no banco, sem depender apenas de tarefas em memória. Nesta etapa haverá um único executor. Ao reiniciar, itens ainda na fila continuam; tarefas que ficaram em processamento são marcadas como interrompidas, com nova tentativa manual, evitando repetir automaticamente uma futura chamada paga. A tomada da tarefa e as transições devem ser atômicas.

Não há requisito de percentual de progresso ou atualização em tempo real: consulta periódica enquanto a caixa estiver aberta é suficiente. A atualização não pode sobrescrever campos em edição.

## Contrato inicial

| Operação | Comportamento proposto |
| --- | --- |
| `POST /api/imports` | Recebe URL, valida formato, persiste e retorna `202` com ID e estado; não aguarda extração |
| `GET /api/imports` | Lista pendências e estados |
| `GET /api/imports/{id}` | Retorna estado, fonte, rascunho e erro compreensível quando houver |
| `PATCH /api/imports/{id}/draft` | Persiste correções sem incluir na biblioteca |
| `POST /api/imports/{id}/confirm` | Confirma rascunho pronto e cria uma única receita, em transação |
| `POST /api/imports/{id}/retry` | Recoloca uma falha na fila por ação explícita |
| `POST /api/imports/{id}/discard` | Descarta pendência não ativa |
| `GET /api/recipes?query=...` | Lista receitas confirmadas e permite busca por título |
| `GET /api/recipes/{id}` | Abre receita confirmada |

Estados: `queued → processing → ready → confirmed`; processamento pode terminar em `failed`; `failed → queued` exige nova tentativa. `queued`, `ready` e `failed` admitem descarte. Cancelamento de processamento ativo fica para a integração real.

Guardar URL original e identidade canônica da publicação, datas, estado, erro sanitizado, rascunho original e versão editada. Reenvio da mesma publicação retorna o registro existente, sem nova extração; confirmação repetida retorna a mesma receita. Descarte não apaga o histórico: reenvio pode reabrir o registro descartado na fila, sem criar duplicata. Alterações concorrentes ao rascunho devem detectar versão desatualizada e pedir recarga, preservando o conteúdo local.

Valores ausentes continuam nulos ou listas vazias no contrato. Evidências e atribuição não devem ser perdidas na revisão. Sem exigir que a pessoa invente informações para salvar.

## Ordem de implementação após aprovação

1. Persistência, estados e API, com testes de transações, duplicatas e recuperação.
2. Executor e adaptador de demonstração, com sucesso, falha e interrupção reproduzíveis.
3. Caixa de entrada, revisão e biblioteca responsivas, compartilhando as mesmas regras da API.
4. Testes integrados e roteiro executável com `uv` local no Windows, com comandos finais e dados de demonstração.

## Aceitação e rota de validação

Ambiente local com `uv`, serviço restrito ao computador de desenvolvimento. Endereço: `http://127.0.0.1:8000`. Comandos e dados de exemplo estão no [roteiro de validação](test-guide.md).

1. Registrar pela API a URL da amostra `https://www.instagram.com/p/DdC8Aw1RQU4/` em modo demonstração. Esperado: ID persistido e indicação explícita de simulação.
2. Fechar o navegador durante o processamento e reabrir a caixa. Esperado: receita pronta para ajustar e ausente da biblioteca.
3. Editar título, um ingrediente e uma etapa, guardar o rascunho, recarregar e confirmar. Esperado: correções preservadas e uma única receita na biblioteca.
4. Reiniciar API e executor; buscar pelo novo título. Esperado: dados e fonte preservados.
5. Reenviar a mesma URL com parâmetros de compartilhamento e repetir a confirmação. Esperado: nenhuma duplicata ou segundo processamento.
6. Executar cenário de falha e interromper o executor em processamento. Esperado: estado compreensível e nova tentativa manual, sem pendência eternamente em processamento.
7. Enviar URL inválida e tentar confirmar um item ainda na fila. Esperado: rejeição sem criar receita na biblioteca.
8. Conferir as telas em largura de celular e desktop, incluindo estado vazio, teclado, foco e ausência de informação.

Reprova se dados desaparecerem, simulação parecer extração real, rascunhos entrarem automaticamente na biblioteca, reenvios duplicarem receitas ou fechamento do navegador interromper o processamento.

## Riscos, exclusões e sequência

Gemini continua sem validação. A demonstração não resolve fidelidade, disponibilidade do Instagram, tempo ou custo. SQLite exige transações curtas e arquivo em disco local; não manter transação aberta durante extração. Tratar texto de receita como conteúdo não confiável na renderização.

Esta entrega antecipou API, banco e web em relação à sequência registrada em DS1 e no guia local. A aprovação autorizou essa antecipação somente no recorte de demonstração, mantendo a prova real aberta.

Fora desta entrega: alteração do APK, downloads reais, chamadas pagas, publicação no miniPC, Docker de produção, DNS, Cloudflare, autenticação de produto, notificações push, funcionamento offline e cancelamento de processamento ativo. Acesso remoto e proteção do serviço precisam de plano antes de exposição externa.

Depois: adaptar Android para encaminhar URLs ao contrato validado; retomar a prova de extração com diagnóstico do erro e orçamento definido; integrar o extrator real e validar o percurso completo. A conectividade do celular e a hospedagem terão validação própria.

Versão pretendida: incremento local de desenvolvimento, sem release do produto nesta história. A versão funcional será definida ao fechar o fluxo real de CV1. Nenhum commit ou push está incluído na aprovação do plano.

## Referências técnicas

Consulta em 2026-09-22; recomendações acima são propostas para este projeto.

- [Templates no FastAPI](https://fastapi.tiangolo.com/advanced/templates/): integração com Jinja2.
- [Tarefas em segundo plano no FastAPI](https://fastapi.tiangolo.com/tutorial/background-tasks/): contexto para separar a requisição do executor; a durabilidade aqui virá do banco e da recuperação explícita.
- [Usos apropriados do SQLite](https://www.sqlite.org/whentouse.html): adequação a aplicações locais e limites de concorrência de escrita.
