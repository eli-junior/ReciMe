---
status: Open
raised: 2026-09-20
decided:
deciders:
  - Navigator
related:
  - CV1
---

# Validar fundação técnica e extração de Reels públicos

## Pergunta

Qual stack web, de ponte Android e de backend oferece o melhor percurso de aprendizado e permite importar, dentro de limites razoáveis de tempo e custo, receitas de Reels públicos a partir da legenda, fala e conteúdo visual?

## Decisão

Pendente para a integração real. A base web validada em DS3 não comprova ainda a aquisição e a extração por URL em produção.

## Evidência necessária

- Recebimento de URL pelo compartilhamento Android.
- Forma permitida e confiável de obter conteúdo de um Reel público para análise.
- Qualidade de extração de título, ingredientes e etapas, incluindo conteúdo em outro idioma.
- Tempo observado, custo por importação e comportamento de falhas.
- Compatibilidade com hospedagem em Docker no miniPC Ubuntu e proteção via Cloudflare.

## Consequências

Não comprometer o projeto com um framework, provedor de IA ou promessa de 15 segundos antes da prova técnica. A primeira entrega continua sem login e exige revisão editável na web antes da entrada na coleção; importações e rascunhos são persistidos previamente.

## Gatilho de revisão

Concluir a prova técnica com Reels públicos reais e um limite de gasto aprovado pelo Navigator.
