# Recomendação técnica — proposta para revisão

## Revisão de sequência aprovada em 20/09/2026

O Navigator aprovou testar primeiro aquisição + IA em um script Python no WSL. Backend, banco, autenticação e máquina de estados abaixo são alternativas futuras, não decisões nem requisitos desta prova. A prova produz JSON e não necessita SQLite ou PostgreSQL. Retirar schema_version do contrato experimental; manter evidence, warnings e null. Kotlin + Compose permanece recomendação. Nutrição/TACO/USDA foi deliberadamente excluída da primeira entrega nas entrevistas e no briefing consolidado.

O roteiro operacional atual está no [README](../../../../../../README.md). Os blocos abaixo preservam a pesquisa original para revisão futura; a sequência desta seção prevalece.

Pesquisa documental em 20/09/2026. As escolhas abaixo são recomendações do Driver, ainda não decisões aceitas nem resultados de benchmark.

## Aplicativo

| Alternativa | Adequação ao projeto | Custo de aprendizado |
| --- | --- | --- |
| Kotlin + Jetpack Compose | Recomendada: foco Android e integração direta com compartilhamento e ciclo de vida | Kotlin e UI declarativa; aproveita a experiência Java |
| React Native | Opção se houver interesse futuro forte em React e múltiplas plataformas | JavaScript/TypeScript, React e integração com Android |
| Flutter | Opção multiplataforma com UI própria | Dart, widgets e integração de plugins com Android |

O foco atual é aprender Android, sem requisito iOS. Por isso proponho Kotlin + Compose. Compose é o toolkit moderno recomendado pelo Android; o recebimento de texto compartilhado usa ACTION_SEND, text/plain e EXTRA_TEXT. Devemos testar tanto abertura fria quanto app já aberto. Fontes: [Compose](https://developer.android.com/compose), [recebimento de dados](https://developer.android.com/develop/ui/compose/sharing/receive), [React Native](https://reactnative.dev/docs/environment-setup), [Flutter](https://docs.flutter.dev/resources/architectural-overview).

## Backend e dados

Proponho Python + FastAPI + Pydantic, aproveitando a experiência do Navigator e validação tipada com OpenAPI. Java/Spring é uma alternativa compatível com sua experiência; a preferência por Python aqui é reduzir mudanças de linguagem no protótipo de extração. [Documentação FastAPI](https://fastapi.tiangolo.com/features/).

Para persistência do produto, proponho PostgreSQL em Docker, com migrações; a prova inicial pode produzir arquivos JSON. Redis, busca vetorial e armazenamento S3 não são necessários para comprovar esta entrega. Um único backend com adaptadores separados para aquisição e IA permite substituir o extrator sem mudar o app.

O app continua na tela de espera, mas a API deve representar uma importação por ID e estados: recebendo, obtendo vídeo, analisando, pronto, falhou ou cancelado. Consultas periódicas permitem recuperar estado após recriação da tela. Cancelamento impede salvar/publicar resultado tardio; não garante estorno de uma chamada de IA já iniciada. Progresso por etapa, sem percentual fictício.

Uso pessoal sem tela de login não significa API pública sem proteção. Proponho credencial revogável provisionada no dispositivo e validada no backend, com HTTPS; o mecanismo exato será validado com a configuração Cloudflare. Chaves de IA ficam apenas no backend, fora do Git e do APK.

## Aquisição e IA

O suporte documentado de Gemini a vídeo inclui arquivo e URL de YouTube. Isso não comprova leitura direta de Reel do Instagram. Proponho obter o arquivo primeiro, enviá-lo junto com a legenda disponível e solicitar saída estruturada. [Vídeo no Gemini](https://ai.google.dev/gemini-api/docs/video-understanding).

O yt-dlp lista Instagram entre os extratores. É candidato para a prova sem cookies/login, não garantia de acesso a qualquer Reel público. Se exigir login ou falhar, registrar falha; testar arquivo fornecido pelo Navigator pode isolar a IA, mas não valida importação por link. [Sites suportados](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

A API oficial da Meta atende contas profissionais e documenta restrições para contas pessoais. A documentação consultada não estabelece um mecanismo universal de baixar qualquer Reel por URL. [Coleção oficial da Meta](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api).

Recomendo Gemini como primeiro provedor experimental por aceitar vídeo e áudio no mesmo modelo. Gemini 2.5 Flash é uma referência estável documentada para a prova, não afirmação de ser o modelo mais novo ou melhor: revalidar disponibilidade antes de executar. Saída estruturada garante formato, não fidelidade. Alternativa: transcrição e quadros enviados separadamente a modelos especializados, com mais etapas e sincronização. [Modelo](https://ai.google.dev/gemini-api/docs/models/gemini-2.5-flash), [saída estruturada](https://ai.google.dev/gemini-api/docs/structured-output).

## Contrato inicial proposto

O resultado da extração é um rascunho, não uma receita salva. Strings ausentes são null; listas sem evidência são vazias. A interface apresenta esses estados como “não informado”. Não persistir essa frase como quantidade numérica.

| Campo | Tipo e regra |
| --- | --- |
| schema_version | Inteiro, inicialmente 1 |
| source | URL original obrigatória; autor e URL da capa opcionais |
| title | Texto ou null; não inventar título culinário não sustentado pela fonte |
| ingredients | Lista ordenada de name, quantity_text e evidence; nome e quantidade podem ser null |
| steps | Lista ordenada de instruction e evidence |
| evidence | Canal caption/audio/visual, trecho literal ou descrição observada e timestamp quando houver |
| warnings | Lista de campos ausentes, ambiguidades e conflitos entre fontes |
| language | pt-BR na saída |

Manter quantidades textuais como “1/2 xícara” ou “a gosto”; normalização numérica não é necessária nesta prova. Uma imagem de uma tigela não sustenta inferir gramas. Tradução deve preservar medidas originais. Conflito entre legenda e fala deve ser sinalizado, não resolvido silenciosamente. Evidências produzidas pela IA também precisam de conferência humana.

Título, ingredientes e etapas são editáveis. Preservar o rascunho original para comparação durante a prova e distinguir correções do usuário. Não exigir que ele invente um dado ausente para concluir a revisão.

## Custos propostos

Tabela consultada para Gemini 2.5 Flash Standard: US$ 0,30 por milhão de tokens de texto/imagem/vídeo; US$ 1,00 para áudio; US$ 2,50 de saída, incluindo raciocínio. [Preços oficiais](https://ai.google.dev/gemini-api/docs/pricing).

Exemplo de planejamento, não medição por minuto: 20.000 tokens visuais/textuais + 2.000 de áudio + 3.000 de saída/raciocínio custariam US$ 0,0155. Vinte chamadas com esse consumo custariam US$ 0,31. Uso real, tentativas adicionais, tamanho e processamento variam; contar tokens e registrar usage do provedor antes de extrapolar. Não inclui aquisição paga, impostos ou infraestrutura.

Proponho teto total de US$ 2 para a primeira rodada, no máximo 20 chamadas, sem repetição automática. Este teto ainda depende de confirmação. Ele deve ser controlado no executor considerando o custo máximo reservado por chamada; alerta do provedor sozinho não garante bloqueio de gastos.

## Ambiente observado

uv, Docker e Node foram encontrados no PATH. Java, adb e Flutter não foram encontrados no PATH; isso não prova ausência de instalações fora dele. Python aponta para o alias WindowsApps, ainda não validado como interpretador. Nenhum SDK foi instalado, daemon Docker testado ou miniPC acessado nesta história.
