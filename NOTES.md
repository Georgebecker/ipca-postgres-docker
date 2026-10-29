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

## 2026-10-29 — Neon no lugar do PostgreSQL em Docker (contorno)

- O **Docker Desktop não funcionou no Windows 11** desta máquina, apesar da configuração
  atender aos requisitos (virtualização e WSL 2). Houve conflito na instalação e o comando
  `docker` não ficou disponível.
- Para não travar o degrau, a solução foi **Neon** (PostgreSQL gerenciado, plano gratuito):
  projeto `ipca-postgres-docker`, organização `George H`, região São Paulo.
- É **contorno temporário**, não mudança de arquitetura: `docker-compose.yml`, `init.sql`,
  `Dockerfile` e `seed.sql` continuam versionados e válidos para quando o Docker voltar.
- Decisão completa, com opções descartadas e critério de revisão, em
  `docs/decisoes/0001-neon-em-vez-do-docker-local.md`. Evidência em
  `docs/evidencias/14-neon-setup.txt`.
- **Pendência criada por isso:** a API lê `POSTGRES_HOST/PORT/USER/PASSWORD/DB`, e o Neon
  entrega `DATABASE_URL`. Enquanto a ponte não existir, os endpoints não conversam com o
  Neon.

## 2026-10-29 — divergência da base sinalizada (7 arquivos com bloco colado)

- Auditoria de estrutura e `.md`: **7 arquivos ficaram com dois documentos dentro de um**,
  porque um bloco novo foi colado por cima do original em vez de substituí-lo —
  `README.md`, `docs/REGRAS_DE_OURO.md`, `meu-loop-agente/{program.md, config_loop.json,
  baseline.json, log.md, system_prompt.md}`. Nada foi perdido: as alterações estão no
  working tree, ainda não commitadas, e o `HEAD` guarda a base íntegra.
- **Bloqueio que era mudo:** `config_loop.json` e `baseline.json` terminaram com dois
  objetos JSON. O verificador parava com `Extra data`, sem dizer onde — quem tentasse
  rodar o loop concluiria que a ferramenta estava com defeito.
- **Corrigido nesta sessão (só a sinalização):** `verificar_iteracao.py` agora detecta
  mais de um objeto JSON no arquivo e diz em que linha o segundo bloco começa, além de
  sugerir o conserto. Mudança localizada em `carregar_json` e no novo
  `localizar_segundo_documento`. _Divergência de propósito em relação ao
  `projeto_loop`_ — a base mostra o erro cru; aqui a mensagem ensina.
- **Pendências (decisão do dono: não corrigir agora):** desduplicar os 7 arquivos,
  restaurar as Partes I–IV de `docs/REGRAS_DE_OURO.md` e trocar a métrica de bundle pelos
  comandos reais do projeto. Enquanto isso, `estado`, `medir` e `verificar` continuam
  parando com código 1 — de propósito, para não medir a métrica errada.
- **Métrica do Degrau 1 definida pelo dono:** endpoints funcionando, 0 → 3
  (`/health`, `/ipca/ultimo`, `/ipca/serie`). É meta absoluta, não percentual.
