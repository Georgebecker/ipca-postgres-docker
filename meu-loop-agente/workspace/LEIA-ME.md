# workspace — campo de ação do agente

Somente o que estiver DENTRO desta pasta pode ser lido e modificado pelo agente
de Loop Engineering.

## O que existe aqui

- `api/` — a API FastAPI (`app/`) e o `Dockerfile`.
- `db/` — os SQL: `init.sql` (estrutura), `seed.sql` (dados) e `verificacao.sql`.
  A subpasta `mysql/` tem o equivalente para o extra opcional de MySQL.
- `scripts/` — `baixar_dados.py`, `gerar_seed.py`, `medir_endpoints.py` e
  `aplicar_sql_nuvem.py`.
- `config.py` — a central de operação (menu do dia a dia).

As pastas de exemplo do modelo original (`app/`, `components/`, `lib/`) foram
removidas: eram do padrão web/Next.js e não têm uso neste projeto.

## Regras

- Tudo aqui pode ser alterado ou revertido a cada iteração. Use Git para ter pontos
  de retorno (commit antes de cada iteração).
- Não coloque segredos (`.env`, chaves, credenciais) aqui.
