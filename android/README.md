# ReciMe Android — demonstração da interface

Aplicativo nativo Kotlin + Jetpack Compose. Fluxo: biblioteca → importação simulada → revisão editável → salvar na sessão → detalhe e busca. A receita é transcrita manualmente da legenda de Guilherme Araujo (@gui.tank), não extraída pelo Gemini.

## Compilar e abrir

Abra esta pasta `android/` no Android Studio. Use JDK 17 ou 21, Android SDK 36 e Build Tools 35.0.0, instalados pelo SDK Manager. Configure o caminho do SDK pelo Android Studio ou por `ANDROID_HOME` no terminal. Execute o módulo `app` em um aparelho/emulador Android 8.0 (API 26) ou superior.

```bash
./gradlew testDebugUnitTest lintDebug assembleDebug
```

APK: `app/build/outputs/apk/debug/app-debug.apk`. Instalação em dispositivo autorizado com depuração USB: `adb install -r app/build/outputs/apk/debug/app-debug.apk`.

As versões estão fixadas nos arquivos Gradle; a combinação AGP/Gradle segue a [documentação Android](https://developer.android.com/build/releases/agp-8-13-0-release-notes), com dependências Compose alinhadas por [BOM](https://developer.android.com/develop/ui/compose/bom).

## Verificação desta implementação

Compilação realizada em 20/09/2026: `testDebugUnitTest lintDebug assembleDebug` terminou com sucesso. Os 7 testes Android passaram. Lint: zero erros e 7 avisos (5 de versões mais novas, 1 sobre regras de backup e 1 de ícone de aplicativo ausente). Esses avisos permanecem pendentes de revisão; não impedem instalar o APK de demonstração. Não havia aparelho ou emulador conectado, portanto aparência, teclado, rotação e interação ainda precisam da validação manual abaixo.

Neste ambiente WSL, o SDK e o cache de compilação foram instalados temporariamente em `/tmp`. Enquanto esses diretórios existirem, reproduza a compilação a partir de `android/` com:

```bash
JAVA_HOME=/home/eli/.sdkman/candidates/java/21.0.7-tem \
ANDROID_HOME=/tmp/recime-android-sdk \
GRADLE_USER_HOME=/tmp/recime-gradle-cache \
./gradlew testDebugUnitTest lintDebug assembleDebug --no-daemon
```

Para uso contínuo, configure o SDK pelo Android Studio em um diretório permanente; os caminhos de `/tmp` não são pré-requisitos do projeto.

## Rota de validação manual

1. Abra **ReciMe · Demo**. Esperado: biblioteca vazia, aviso de demonstração e botão de importar.
2. Toque em **Importar receita**. O link de exemplo já está preenchido. Troque por `https://example.com`: a importação deve exibir erro e permanecer nessa tela.
3. Use `https://www.instagram.com/p/DdC8Aw1RQU4/`. Inicie e cancele durante o progresso. Espere alguns segundos: a revisão não deve abrir nem surgir uma receita salva.
4. Repita e deixe a simulação terminar. Esperado: revisão da fraldinha; título, ingredientes e etapas editáveis. Quantidade de fraldinha aparece como “não informado” enquanto vazia.
5. Altere o título para “Almoço de domingo”, adicione/remova um ingrediente e uma etapa. Toque em **Salvar na sessão**. Confira as alterações no detalhe e a atribuição da fonte.
6. Volte à biblioteca e busque `almoco`. Deve encontrar a receita mesmo sem acento. Busque `sopa`: deve aparecer o estado sem resultados.
7. Abra e edite a receita salva. Salve novamente: deve continuar existindo apenas uma receita.
8. Gire o dispositivo durante revisão e importação: o ViewModel deve manter a sessão. Teste teclado aberto, rolagem até salvar e tamanho de fonte aumentado.
9. Force o encerramento do processo e reabra. A biblioteca deve voltar vazia; não há persistência nesta etapa.

Aprovação: fluxo completo utilizável, edições preservadas na sessão, cancelamento sem resultado tardio, busca funcionando e nenhuma informação ausente inventada. Reprovação: travamento, perda de edição ao girar, controles inacessíveis, duplicação ao editar ou simulação apresentada como extração real.

## Limites desta entrega

Qualquer URL válida abre o mesmo exemplo e mantém a fonte verdadeira desse exemplo. Não há chamadas de rede, permissão de internet, integração com Gemini/backend, compartilhamento Android ou armazenamento permanente. Não é uma implementação do modo offline do produto. O Gemini permanece pendente após `ClientError` na prova anterior.

Biblioteca e rascunho vivem em um ViewModel, preservando rotação mas não morte do processo. A interface está separada dos dados de exemplo e das transições de estado; a integração futura deverá substituir a simulação. O Navigator informou ter testado o APK, decidiu manter a interface como está e autorizou commit e sincronização. O relato não detalhou cada cenário do roteiro, portanto a validação individual de rotação, teclado e acessibilidade permanece sem registro.
