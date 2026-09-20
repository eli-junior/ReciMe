# Aquisição real e demonstração Android

O downloader passou a aceitar `/p/` e verificar áudio e vídeo com ffprobe. O Reel `DdC8Aw1RQU4` foi adquirido sem login em 3,074 segundos: 25.430.648 bytes, 119,8 segundos, vídeo H.264 e áudio AAC. A decodificação completa não apresentou erros.

O Navigator autorizou uma extração Gemini com teto de US$ 2. Upload/processamento funcionaram; geração retornou `ClientError`, sem receita ou métricas de consumo. O detalhe do erro não foi preservado. Não houve nova geração; a consulta de metadados confirmou acesso ao modelo. Integração adiada pelo Navigator; custo ainda exige conferência no painel.

Foi aprovada e implementada a demonstração Android em Kotlin + Compose, com biblioteca, busca, importação simulada cancelável, revisão editável e dados em memória. A amostra foi transcrita da legenda, não extraída por IA. O Navigator informou ter testado o APK, pediu manter a interface e autorizou commit e sincronização com o remoto.

Verificação: 18 testes Python e 7 testes Android passaram; `lintDebug` e `assembleDebug` concluíram. Lint: zero erros, 7 avisos descritos no README Android. Não havia dispositivo conectado ao ambiente do Driver. O relato do Navigator não detalha cada cenário manual.

Revisão: nenhuma refatoração bloqueadora para a demonstração; dados, estado e telas estão separados. Ícone, regras de backup e versões de dependências ficam para revisão futura. Dados temporários e ausência de backend fazem parte do recorte aprovado. Não há versão do produto encerrada, portanto changelog permanece sem release.

Próximos passos: definir a próxima entrega com o Navigator; persistência e integração permanecem pendentes. Segredos, vídeos, relatórios locais e APKs ficam fora do Git.
