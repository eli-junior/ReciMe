---
status: Decided
raised: 2026-09-22
decided: 2026-09-22
deciders:
  - Navigator
related:
  - CV1
  - CV1.DS2
---

# Interface web e ponte Android

## Decisão

O Navigator mudou o escopo: toda a interface de receitas será web. O Android recebe o compartilhamento do Instagram e encaminha a URL à API. Ao acessar a web, a pessoa encontra novas receitas para ajustar.

## Consequências

- A ponte informa aceitação ou falha de envio, sem aguardar a extração.
- O backend persiste a importação e processa a extração sem depender de clientes abertos.
- A web mostra processamento, falha e receitas prontas para revisão; edição, coleção e busca ficam na web.
- Importações e rascunhos são persistidos antes da revisão. Entrar na coleção exige confirmação da pessoa.
- A demonstração Android permanece como histórico; biblioteca e revisão nativas deixam de orientar a implementação futura.
- Permanecem uso pessoal, pt-BR, Reels públicos, fidelidade à fonte, dependência do backend e hospedagem planejada no miniPC.

## Em aberto

O Navigator aprovou o [plano DS3](../../roadmap/cv1-importar-receitas-de-reels/cv1-ds3-caixa-de-entrada-web/index.md): FastAPI/Pydantic, páginas Jinja2 com CSS e JavaScript, SQLite e executor separado com fila persistida para a demonstração local. Reenvios reutilizam a importação; falhas permitem nova tentativa manual. Em seguida, orientou usar `uv` local no Windows, sem WSL.

Reaproveitamento do Android, integração real, cancelamento ativo e operação em produção continuam para planos próprios. Notificações push não foram solicitadas. A viabilidade da extração continua pendente.

## Validação futura

Compartilhar no Android, fechar o app, acessar a web, encontrar a importação, ajustar a receita e confirmar sua entrada na coleção. Recarregar e buscar pelo título. Esta decisão registra escopo; não atesta implementação ou testes desse fluxo.
