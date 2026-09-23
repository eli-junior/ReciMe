---
code: CV1
level: Value
status: Active
status_reason: base web persistente validada; ponte Android e extração real pendentes
updated: 2026-09-22
related:
  - ../../decisions/records/2026-09-20T0000Z-validar-fundacao-tecnica-e-extracao.md
---

# CV1 — Importar e guardar receitas de Reels

## Intenção

Permitir que o Navigator capture uma receita de um Reel público, confirme os dados extraídos, salve-a no seu backend e a recupere depois.

## Escopo

Inclui uma ponte Android que recebe a URL por compartilhamento e a envia à API, processamento independente no backend com IA em nuvem, persistência de importações e rascunhos, caixa de entrada web com novas receitas para ajustar, revisão editável e coleção web com busca por título.

## Condição de encerramento

O Navigator compartilha um Reel público real pelo Android, recebe confirmação de envio e pode fechar o app. Ao acessar a web, encontra a importação e seu estado, revisa a receita pronta, corrige os campos, salva na coleção e a encontra por busca após recarregar a página. Reprova se a importação se perder, depender do app aberto ou entrar na coleção sem revisão.

## Próxima decomposição

- [DS1 — Fundação e viabilidade](cv1-ds1-fundacao/index.md): aquisição validada em um caso; extração Gemini pendente após `ClientError`.
- [DS2 — Demonstração da interface Android](cv1-ds2-interface/index.md): implementada e testada pelo Navigator. A importação é simulada e os dados duram apenas durante a sessão.
- [DS3 — API e caixa de entrada web](cv1-ds3-caixa-de-entrada-web/index.md): plano aprovado; implementação com persistência real e extração simulada, testes locais concluídos e validação manual pendente.

A DS2 permanece como evidência histórica. A DS3 propõe a base web e de persistência. Ponte Android e extração real integrada terão entregas posteriores. As demonstrações não encerram CV1.

## Fora de escopo

Autenticação, funcionamento offline, nutrição, coleções, planejamento de refeições, lista de compras, modo cozinha e assistente culinário.
