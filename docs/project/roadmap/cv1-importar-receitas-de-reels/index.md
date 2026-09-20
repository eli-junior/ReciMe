---
code: CV1
level: Value
status: Active
status_reason: aquisição real validada em um caso; demonstração Android testada; integração e persistência pendentes
updated: 2026-09-20
related:
  - ../../decisions/records/2026-09-20T0000Z-validar-fundacao-tecnica-e-extracao.md
---

# CV1 — Importar e guardar receitas de Reels

## Intenção

Permitir que o Navigator capture uma receita de um Reel público, confirme os dados extraídos, salve-a no seu backend e a recupere depois.

## Escopo

Inclui o app Android, recebimento de URL por compartilhamento, pipeline de extração com IA em nuvem, revisão editável, persistência no backend e listagem com busca por título.

## Condição de encerramento

O Navigator consegue concluir o fluxo com um Reel público real, corrigir os campos quando necessário, salvar a receita e encontrá-la novamente por busca.

## Próxima decomposição

- [DS1 — Fundação e viabilidade](cv1-ds1-fundacao/index.md): aquisição validada em um caso; extração Gemini pendente após `ClientError`.
- [DS2 — Demonstração da interface Android](cv1-ds2-interface/index.md): implementada e testada pelo Navigator. A importação é simulada e os dados duram apenas durante a sessão.

Captura por compartilhamento Android, extração integrada, backend e persistência continuam futuros. A demonstração não encerra CV1.

## Fora de escopo

Autenticação, funcionamento offline, nutrição, coleções, planejamento de refeições, lista de compras, modo cozinha e assistente culinário.
