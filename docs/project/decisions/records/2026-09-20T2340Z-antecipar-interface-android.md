---
status: Decided
raised: 2026-09-20
decided: 2026-09-20
deciders:
  - Navigator
related:
  - CV1.DS2
---

# Antecipar a interface Android

Após falha da geração Gemini, o Navigator pediu deixar essa integração para depois e aprovou Kotlin + Jetpack Compose para desenvolver a interface com dados de exemplo.

A demonstração permite importar de forma simulada, revisar, editar, salvar na sessão e buscar por título. Ela não comprova extração nem cria compromisso de funcionamento offline do produto. O Navigator testou o APK e decidiu manter a interface como está por enquanto.

A decisão de stack mobile está aceita; backend, banco, provedor definitivo e viabilidade da extração permanecem abertos. Retomar Gemini quando houver orientação para essa frente, começando por preservar os detalhes do `ClientError` e conferir faturamento da tentativa anterior.

## Mudança de direção — 2026-09-22

A demonstração e sua validação permanecem como histórico. O Navigator redefiniu o produto: a interface de receitas será web, e o Android será apenas uma ponte para enviar URLs à API. Biblioteca e revisão nativas deixam de orientar a implementação futura.
