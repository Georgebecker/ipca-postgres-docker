# NOTES — decisões do projeto

## 2026-10-29 — criação a partir da base

- Projeto criado com `scripts\criar_projeto_base.ps1` do `projeto_loop`
  (`-Nome ipca-postgres-docker -Titulo "IPCA Postgres Docker"`). O gerador já copiou
  Regras de Ouro, ganchos `.githooks`, `.env`/`.env.example`, `meu-loop-agente/` e o
  agente `.github/agents/deepseek-flash.agent.md`.
- `.env` local veio da base e **não foi alterado** (pertence ao dono). Ele ainda aponta
  `DB_URL` para SQLite; a troca para PostgreSQL é decisão do dono.
- `docker-compose.yml` **não** foi criado neste ciclo: o Docker não está instalado nesta
  máquina, então não haveria como validar o serviço. Primeiro ciclo do loop deve ser
  "subir o PostgreSQL em Docker e provar com `docker compose ps`".
- `meu-loop-agente/program.md` e `config_loop.json` seguem o exemplo Next.js da base
  (métrica de tamanho de bundle). São arquivos do humano e precisam da métrica real do
  projeto antes do primeiro ciclo.
