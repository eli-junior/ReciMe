# Validação do Navigator e roteiro da prova

Atualização: após aprovação da sequência revisada, a CLI foi implementada em `probe.py` com dependências fixadas por `uv.lock`. O [README](../../../../../../README.md) contém comandos atuais e limitações. As seções abaixo descrevem o planejamento original; teste Android permanece futuro. A CLI não implementa teto acumulado de gastos nem proteção de redirects de um servidor público. Ainda não há evidência de extração real.

## Validação desta história documental

1. Abra `recomendacao.md` nesta pasta. Compare Kotlin, React Native e Flutter e confira se o foco Android/Java sustenta a escolha proposta.
2. Revise o contrato usando este exemplo sintético: “Misture 2 ovos com farinha e asse”. Esperado: ovos = “2”, farinha = null; não criar temperatura, duração ou quantidade de farinha. A interface futura mostra “não informado”.
3. Confira que vídeo, áudio e legenda entram na prova, e que revisar/editar antecede salvar.
4. Leia o roteiro abaixo e confira a separação entre falha de acesso e erro de extração.

Aprovação: recomendação compreensível, contrato fiel às decisões e roteiro reproduzível após a preparação indicada. Falha: inferências apresentadas como fatos, teste por arquivo apresentado como sucesso por link, custo ou latência tratados como medidos sem execução.

## Prova futura — pré-requisitos

Esta seção é um protocolo; não há script de extração ou APK implementado nesta TS1. A próxima história deverá fornecer os comandos exatos e fixar versões do executor, SDK e modelo.

Precisaremos de chave Gemini configurada localmente como segredo, teto de US$ 2 aceito (ou outro valor), e cinco Reels públicos: receita completa na legenda; informação apenas falada; quantidade apenas visual; receita incompleta; receita em outro idioma. O Navigator pode fornecer URLs habituais. Preparar gabarito manual com trechos/timestamps antes de avaliar a IA.

## Sequência reproduzível

1. Aquisição: em ambiente preparado com yt-dlp, executar `yt-dlp --no-playlist --skip-download --dump-single-json URL_DO_REEL`. Registrar versão, sucesso/erro, duração e disponibilidade de legenda/mídia, sem publicar URLs temporárias de mídia em logs compartilhados.
2. Baixar vídeo de cada caso acessível para diretório temporário com `yt-dlp --no-playlist -o "video.%(ext)s" URL_DO_REEL`, usando uma pasta separada por caso. Não adicionar cookies/login se houver bloqueio; registrar o resultado.
3. Extração: executor futuro recebe arquivo, legenda, esquema e instrução de não inferir; envia ao Gemini, valida JSON e grava resultado + métricas. Registrar tempos de aquisição, upload/processamento e geração separadamente, modelo, configuração e consumo. Usar timeout experimental de 120 segundos por tentativa, sem confundi-lo com SLA do produto.
4. Repetir cada caso duas vezes, sem cache. Comparar resultados ao gabarito; não corrigir o rascunho antes da avaliação.
5. Verificar entradas negativas: URL fora do Instagram, Reel indisponível, resposta inválida do modelo e cancelamento. Rejeitar hosts inesperados e destinos privados antes de qualquer download; validar redirecionamentos no executor futuro.
6. Prova Android posterior: compartilhar URL pelo Instagram, com app fechado e aberto. Esperado: mesma URL apresentada na importação; cancelamento não produz receita salva. Um Intent artificial não substitui esse teste no aplicativo real.

## Critérios propostos da prova

- Acesso: registrar resultado de todos os cinco links; qualquer falha impede declarar suporte integral à amostra.
- Fidelidade: zero quantidades, tempos ou etapas inventados; capturar pelo menos 90% dos fatos do gabarito, contando cada ingrediente/quantidade/etapa explicitamente verificável como fato. Todos os campos críticos apenas visuais ou falados devem ser capturados.
- Ausências: todos os dados ausentes do gabarito continuam ausentes; conflitos ficam sinalizados.
- Estrutura: 100% das respostas aceitas passam pela validação do contrato. Falhas do modelo são registradas, não descartadas da estatística.
- Latência: relatar mediana, máximo, tamanho/duração e todas as falhas; sem promessa de 15 segundos. O Navigator avalia o tempo aceitável após ver os números.
- Custo: respeitar teto aprovado, contabilizar chamadas falhas cobradas e parar quando não houver saldo reservado suficiente.

Se a IA passar usando arquivo manual, mas o acesso Instagram falhar, a conclusão é “extração viável; importação por link não comprovada”. Não substituir automaticamente o escopo do produto.

## Evidência atual

Pesquisa em documentação oficial e inspeção de ferramentas no PATH. Nenhuma inferência paga, download de Reel ou teste Android executado. Testes funcionais: não aplicáveis a esta entrega documental; a prova real permanece pendente.
