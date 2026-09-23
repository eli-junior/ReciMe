# Validar a API e a caixa de entrada web

Esta entrega usa persistência real e uma amostra manual. Não acessa o Instagram, não chama Gemini e não exige FFmpeg ou chave de IA. A ponte Android ainda não está integrada.

## Iniciar no Windows com uv local

Em um terminal PowerShell:

```powershell
cd D:\projetos\ReciMe
uv sync
uv run uvicorn recime.app:app --host 127.0.0.1 --port 8000
```

Em outro terminal, na mesma pasta:

```powershell
cd D:\projetos\ReciMe
uv run python -m recime.worker
```

Abra <http://127.0.0.1:8000>. Mantenha os dois terminais abertos; Ctrl+C encerra cada serviço. Se o Driver já deixou ambos rodando, basta abrir a URL. Não abra outro servidor na mesma porta. Um segundo executor para o mesmo banco é recusado.

O banco fica em `data/recime.sqlite3`; API e executor precisam apontar para o mesmo arquivo. Os dados são ignorados pelo Git. O executor separado continua trabalhando com o navegador fechado. Sem executor, a importação permanece na fila. Sem API, a interface não funciona.

## Percurso principal

1. Na caixa de entrada, clique em **Usar link de exemplo** e **Adicionar à caixa**. Alternativamente, ajuste a receita de exemplo já pendente, se o Driver a tiver preparado.
2. A URL é `https://www.instagram.com/p/DdC8Aw1RQU4/`. Veja **Na fila** ou **Preparando receita** e feche a aba. Reabra após alguns segundos: deve aparecer uma nova receita pronta para ajustar. A contagem considera somente receitas prontas.
3. Abra **Ajustar receita**. Mude o título para `Almoço de domingo`, ajuste um ingrediente e uma etapa. Adicione e remova um item para conferir a edição de listas.
4. Clique em **Guardar rascunho** e recarregue a página. As alterações devem permanecer; a biblioteca ainda deve estar vazia.
5. Clique em **Salvar na biblioteca**. Confira a receita, fonte e os campos ausentes exibidos como `não informado`.
6. Na biblioteca, busque por `almoco`. A busca ignora caixa e acentos.
7. Pare e reinicie os dois serviços usando os mesmos comandos. A receita deve continuar disponível.
8. Reenvie o link com `?igsh=teste` no fim: a interface deve informar que a receita já está na biblioteca, sem duplicá-la.

O conteúdo é identificado como demonstração em todas as telas. Outra URL válida não recebe a receita de exemplo: termina em falha explicando que não há amostra.

## Falha, nova tentativa e interrupção

Para repetir a amostra desde o começo sem apagar sua biblioteca, use outro banco de validação. Pare os serviços e defina a mesma variável em **ambos** os terminais antes de iniciar novamente:

```powershell
$env:RECIME_DB = 'D:\projetos\ReciMe\data\validacao-falha.sqlite3'
```

Na tela inicial, preencha o link de exemplo; em **Opções da demonstração**, escolha **Falhar na primeira tentativa**. Depois do envio, abra a falha e clique em **Tentar novamente**. A segunda tentativa deve disponibilizar a receita para revisão. Reenvios mantêm o cenário original: não alteram uma importação existente.

Para observar a fila e a interrupção, use um novo arquivo, como `data\validacao-interrupcao.sqlite3`, nos dois terminais. Inicie o executor com:

```powershell
uv run python -m recime.worker --delay 30
```

Envie o exemplo e, quando aparecer processamento, encerre o executor com Ctrl+C. A tarefa deve ficar com erro de interrupção. Reinicie o executor e use a nova tentativa manual. No caso de encerramento forçado do processo, a recuperação ocorre quando o executor é reiniciado; a aplicação não repete a tarefa automaticamente. Esse caso também é exercitado pelo teste automatizado com encerramento real de subprocesso.

Para voltar ao banco padrão, pare os serviços e remova a variável nos dois terminais antes de reiniciar:

```powershell
Remove-Item Env:RECIME_DB -ErrorAction SilentlyContinue
```

Descartar esconde a pendência; reenviar o mesmo link reabre seu registro e prepara um novo rascunho. Não há cancelamento enquanto estiver processando.

## Duas abas e uso visual

Abra o mesmo rascunho em duas abas. Guarde uma alteração na primeira e tente guardar outra na segunda. A segunda deve avisar sobre conflito, mantendo o texto na tela para cópia antes de recarregar. A revisão não recebe atualizações automáticas que possam substituir o texto digitado. Alterações ainda não guardadas disparam o aviso de saída do navegador.

Confira em janela larga e estreita: navegação, lista, campos, botões, texto longo e ausência de rolagem horizontal. Percorra o formulário com Tab e confira foco visível. A confirmação visual pelo Navigator continua necessária: não havia navegador conectado à ferramenta de inspeção do Driver nesta sessão.

## API e testes

Envio equivalente à futura ponte Android, em PowerShell:

```powershell
$body = @{ url = 'https://www.instagram.com/p/DdC8Aw1RQU4/' } | ConvertTo-Json
$importacao = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/api/imports' -ContentType 'application/json' -Body $body
$importacao
Invoke-RestMethod -Uri ('http://127.0.0.1:8000/api/imports/' + $importacao.id)
```

Contrato JSON em <http://127.0.0.1:8000/openapi.json>. Edição e confirmação exigem a versão atual do rascunho; estados inválidos ou edição desatualizada retornam `409`. Reenvio e confirmação repetidos não duplicam a receita. Formato inválido retorna `422`; registro ausente retorna `404`.

```powershell
uv run pytest -q
node --check recime/static/app.js
```

Evidência inicial: 37 testes passaram no Windows, incluindo os testes anteriores da prova. Dois avisos de depreciação vêm de dependências do cliente de testes (httpx/Starlette e BlockingPortal/AnyIO), sem falha funcional observada. Não foram feitas chamadas de IA ou aquisição real.

## Aceitação

Aprovar se o link persiste, o processamento independe do navegador, as correções sobrevivem ao reinício, a revisão é obrigatória e os reenvios não duplicam receitas. Reprovar se houver perda de dados, receita salva sem confirmação, simulação apresentada como extração real, conflito sobrescrito silenciosamente ou interface que impeça concluir o percurso.

Esta validação é local, sem publicação externa. Após seu relato, seguem revisão, documentação de encerramento e proposta de histórico; nenhum commit ou push foi autorizado nesta etapa.
