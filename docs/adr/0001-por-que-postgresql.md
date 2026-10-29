# ADR 0001 — Por que PostgreSQL neste degrau

- **Status:** aceito
- **Data:** 2026-10-29
- **Decisor:** George Becker (dono do projeto)
- **Contexto do degrau:** Degrau 1 da trilha — aprender modelagem relacional, Docker e seed

## Contexto

O objetivo do degrau é guardar a série histórica do IPCA (SGS 433, do Banco Central) em
um banco local, com carga repetível e consultas SQL prontas. A série tem uma
característica que decide quase tudo: **uma linha por mês, com data única**, e consultas
do tipo "os meses mais recentes" e "o valor de um mês específico". O volume é pequeno
(563 linhas hoje) e a leitura é muito mais frequente que a escrita.

Três alternativas foram consideradas antes de escrever a primeira linha de `init.sql`.

## Alternativas consideradas

| Alternativa | Por que foi descartada |
|---|---|
| **SQLite** (arquivo local) | Não tem `NUMERIC` de verdade, não tem usuário/senha, não roda em container próprio — e o degrau existe para treinar Docker e `docker-compose`, não para fugir dele. |
| **MySQL / MariaDB** | Atenderia ao mesmo caso, mas `docker-compose` com PostgreSQL é o padrão da trilha, e tipos como `NUMERIC(10,4)` e `CHECK` funcionam sem surpresa. Trocar de banco a cada degrau impediria comparar. |
| **Arquivo CSV / planilha** | Não tem constraint, nem índice, nem `UNIQUE`. Justamente o que este degrau quer ensinar — a planilha aceita duas linhas de janeiro/2024 sem reclamar. |

## Decisão

Usar **PostgreSQL 16 em Docker**, com `NUMERIC(10,4)` para o valor, `DATE` com `UNIQUE`
para a competência e o índice `idx_ipca_data_desc`.

## Consequências

**Positivas**

- `UNIQUE` em `data` é a garantia que a planilha não dava: carregar o mesmo mês duas
  vezes é impossível, e é isso que dá sentido ao `ON CONFLICT (data) DO NOTHING` do seed.
- `NUMERIC` preserva `0.42` exatamente; `FLOAT` acumularia erro binário ao somar 561 meses.
- O container com volume nomeado (`pgdata`) sobrevive a `docker compose down`.
- A API fala com o banco pela rede do Compose, usando o nome do serviço (`postgres`),
  o que é o mesmo padrão de qualquer projeto maior.

**Negativas / custo assumido**

- Exige Docker instalado — e isso já custou tempo: a máquina onde a base nasceu não tinha
  Docker, então banco e API foram validados em outro ambiente.
- É mais peça para manter do que SQLite: container, volume, porta, healthcheck.
- Não há migração de schema (sem Alembic): mudar `init.sql` exige recriar o volume e
  reaplicar o seed.

## O que eu sei hoje e não sabia antes de rodar

A escolha poderia ter sido escrita no Dia 2, mas teria sido justificativa imaginada. Só
depois de subir o banco e carregar os dados ficou claro que (a) o `UNIQUE` é o que torna
a recarga segura, (b) o `CHECK` em `tipo` pegou valores inválidos antes de chegarem à
API, e (c) o healthcheck do container é o que impede a API de subir no escuro. Um ADR
escrito antes disso seria cópia de manual, não registro de decisão.
