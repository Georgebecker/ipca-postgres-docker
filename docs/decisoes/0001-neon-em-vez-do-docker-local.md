# Decisão 0001 — Usar Neon em vez do PostgreSQL em Docker (temporariamente)

- **Data:** 2026-10-29
- **Situação:** aceita, com prazo de validade
- **Quem decidiu:** George Becker (dono do projeto)

## Contexto

O Degrau 1 existe para treinar **modelagem relacional, Docker e seed**. O plano original era
um PostgreSQL 16 local, subido por `docker-compose`, com `init.sql` e `seed.sql` — e esse
plano está inteiro no repositório (`docker-compose.yml`, `init.sql`, `seed.sql`, `Dockerfile`).

O problema: **o Docker Desktop não funcionou no Windows 11 desta máquina**, apesar da
configuração atender aos requisitos (virtualização habilitada e WSL 2 instalado). Houve
conflito na instalação que não se resolveu com as tentativas usuais, e o comando `docker`
não ficou disponível no terminal.

Sem banco, o degrau para: não há onde criar a tabela, nem carregar o seed, nem testar os
endpoints.

## Opções consideradas

**1. Insistir no Docker Desktop (reinstalar, mexer em WSL/Hyper-V, antivírus)**

- *Prós:* mantém o plano original; tudo local, gratuito, reproduzível por qualquer pessoa;
  é justamente a habilidade que o degrau quer treinar.
- *Contras:* o tempo de diagnóstico é imprevisível; um problema de ambiente pode consumir
  dias e esconder o assunto real (SQL e modelagem); o risco de piorar outras coisas na
  máquina é real.

**2. Instalar o PostgreSQL nativo no Windows**

- *Prós:* simples, sem virtualização; um instalador e um serviço.
- *Contras:* também não treina Docker; cada máquina exigiria configuração manual, então o
  projeto deixa de ser "reproduzível com um comando".

**3. Neon — PostgreSQL gerenciado, plano gratuito**

- *Prós:* zero instalação; é PostgreSQL de verdade (não uma imitação), com `NUMERIC`,
  `CHECK`, `UNIQUE` e índice funcionando igual; a conexão vem por uma URL; permite seguir
  estudando modelagem e SQL imediatamente.
- *Contras:* **não exercita Docker**, que é objetivo do degrau; depende de internet; o plano
  gratuito tem limites de uso e de espaço; os dados ficam fora da máquina.

**4. SQLite**

- *Contras:* não tem `NUMERIC` de verdade, nem usuário/senha, nem container. Justamente o
  que o degrau quer ensinar — descartado.

## Escolha

**Neon**, para não perder tempo com um problema de ambiente. É uma decisão de **contorno**,
não de arquitetura: o objetivo era aprender modelagem e SQL, e o Neon permite isso hoje,
enquanto o Docker continua pendente.

Registro explícito: **o Docker não foi abandonado**. O `docker-compose.yml`, o `init.sql`,
o `Dockerfile` e o `seed.sql` continuam versionados e válidos. Quando o Docker funcionar, o
projeto volta a rodar local sem reescrever nada.

## Consequência

- O degrau segue: a tabela `ipca` foi criada no Neon e recebeu os **563 registros**
  (561 meses reais + 2 fictícios), conferidos por três consultas — ver
  `docs/evidencias/15-neon-tabela-populada.txt`.
- **Perde-se, por ora, a prática de Docker** — a parte "containers, volume e healthcheck"
  fica sem exercício real e precisa ser retomada.
- **A API ainda não fala com o Neon.** Ela lê `POSTGRES_HOST`, `POSTGRES_PORT`,
  `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`; o Neon entrega `DATABASE_URL`.
  Enquanto essa ponte não existir, os endpoints continuam servindo o banco local.
- O `.env` passou a ter as duas configurações (local e Neon), o que permite alternar sem
  apagar nada.
- O repositório ganhou arquivos do CLI da Neon (`neon.ts`, `package.json`), que são de
  configuração e não guardam segredo.

## O que eu faria diferente

- **Se o projeto crescer:** com mais de um ambiente (local e nuvem), vale uma flag explícita
  no `.env` — por exemplo `BANCO=postgres | neon` — em vez de decidir pela presença de uma
  variável. Foi assim que o `BANCO=postgres|mysql` já resolveu o caso do MySQL.
- **Quando revisar:** assim que o Docker funcionar nesta máquina, ou antes de qualquer
  medição de desempenho (latência de rede não é comparável com banco local).
- **O que evitaria repetir:** começar o degrau com um pré-requisito de ambiente não
  verificado custou tempo. Na próxima trilha, o primeiro passo é provar o ambiente com um
  comando (`docker run hello-world`), antes de escrever a primeira linha de SQL.
