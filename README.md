# IPCA Postgres Docker

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-green)
![Status](https://img.shields.io/badge/status-rascunho-orange)

Quero ter os dados públicos do **IPCA** (a inflação oficial medida pelo IBGE) dentro de
um **PostgreSQL em Docker**, com carga repetível e consultas SQL prontas — sem depender
de planilha baixada à mão. Hoje o repositório é só o esqueleto: ainda não há ETL,
schema nem container.

## Classificação

| Campo | Valor |
|---|---|
| **Propósito** | Guardar a série do IPCA em PostgreSQL local (Docker) de forma reprodutível, para estudar modelagem, carga e consulta de dados públicos. |
| **Maturidade** | Rascunho — base criada em 29/10/2026; sem ingestão, schema, `docker-compose` ou testes. |
| **O que está sendo treinado** | Modelagem relacional, SQL analítico, Docker, ingestão e limpeza de dados públicos (IBGE/SIDRA) e Loop Engineering. |
| **Quem usaria** | Estudantes e analistas que querem um ambiente local de IPCA para praticar SQL e comparar com outras fontes. |

## Metodologia Loop

Este projeto não foi feito no "achismo": ele nasce do modelo
[`projeto_loop`](https://github.com/Georgebecker/projeto_loop) e segue **Loop Engineering**
— hipótese, uma mudança pequena, teste, métrica real e decisão **ACEITO/REJEITADO**.

O contrato vive em `meu-loop-agente/` (`program.md`, `config_loop.json`,
`baseline.json` e `verificar_iteracao.py`), e cada ciclo é registrado em
[`meu-loop-agente/log.md`](meu-loop-agente/log.md). O agente só altera
`meu-loop-agente/workspace/`; regras e configuração são do humano.

## O que tem aqui

- `docs/REGRAS_DE_OURO.md` — regras de postura, processo e técnica do projeto.
- `meu-loop-agente/` — contrato do loop, verificador, linha de base e log.
- `.github/agents/deepseek-flash.agent.md` — agente **DeepSeek Flash** com as regras deste
  repositório; selecione-o no seletor de agentes do Chat.
- `.env` / `.env.example` — configuração local (o `.env` nunca vai ao git).
- `.githooks/` — bloqueiam `.env` e segredo no commit **e** no push.
- `data/raw`, `data/processed`, `data/descartados` e `notebooks` — pastas vazias (só `.gitkeep`).

```
ipca-postgres-docker/
├── .env / .env.example
├── .githooks/
├── .github/agents/deepseek-flash.agent.md
├── docs/REGRAS_DE_OURO.md
├── meu-loop-agente/          # contrato, verificador, log, workspace/
├── data/{raw,processed,descartados}/
├── notebooks/
├── README.md
└── requirements.txt
```
# ipca-postgres-docker (Termômetro)

## O que é

API que consulta a série histórica do IPCA (SGS 433, Banco Central) armazenada em
PostgreSQL rodando em Docker. "SGS" é o Sistema Gerenciador de Séries Temporais do Banco
Central, e a série 433 é a variação mensal do IPCA.

Três rotas, e o resultado de cada uma:

```console
$ curl http://localhost:8000/health
{"status":"ok","postgres":"ok","versao_postgres":"PostgreSQL 16.x"}

$ curl http://localhost:8000/ipca/ultimo
{"data":"2099-02-01","valor":2.3456,"tipo":"ficticio"}

$ curl "http://localhost:8000/ipca/serie?tipo=real"
[{"data":"1980-01-01","valor":6.62,"tipo":"real"},
 {"data":"1980-02-01","valor":4.62,"tipo":"real"}, ...]
```

O `/ipca/ultimo` devolver **2099** é proposital: os dois registros fictícios estão no fim
da linha do tempo, então são os mais recentes. É o teste de que a ordenação funciona.

## Por que existe
É o Degrau 1 de uma trilha de 5 projetos pequenos que, juntos, formam as peças de um projeto final chamado "Encurtador de Links". Este degrau treina modelagem de banco relacional, Docker e seed.

## Onde esta técnica aparece no projeto final

No projeto final (Encurtador de Links), o PostgreSQL guarda os links e as campanhas. A
modelagem aprendida aqui é a mesma: uma tabela com chave própria (`id`), uma coluna de
negócio com `UNIQUE` (ali o código curto do link; aqui a competência mensal), valores
tipados com precisão (`NUMERIC`, não `FLOAT`) e um índice pensado para a consulta mais
frequente. O Docker e o seed também se repetem: subir banco com um comando e poder
recarregar os dados do zero é o que torna o projeto reproduzível.

## Estrutura de pastas
- `.githooks/` — ganchos que bloqueiam segredo no commit e no push.
- `docs/` — regras do projeto e guia da base.
- `meu-loop-agente/` — contrato, config, baseline, log, verificador e system prompt.
- `meu-loop-agente/workspace/` — única pasta onde o agente atua.
- `meu-loop-agente/workspace/db/` — `init.sql` (modelagem), `seed.sql` (carga) e `verificacao.sql`.
- `meu-loop-agente/workspace/scripts/` — `baixar_dados.py`, `gerar_seed.py` e `medir_endpoints.py`.
- `meu-loop-agente/workspace/api/` — a API FastAPI (`app/`) e o `Dockerfile`.
- `data/raw/` — o JSON original do Banco Central (não se edita).
- `data/processed/` — dados tratados (ainda vazio).

## Como rodar

### Modo rápido: o instalador

```powershell
python instalar.py
```

Um menu em português guia a instalação: confere o Docker, cria o `.env` perguntando a
senha, sobe o banco, cria a tabela, carrega os dados, sobe a API e testa os 3 endpoints.
A opção `8` faz tudo na ordem; a `9` desinstala explicando antes o que será apagado.

### Modo manual

Pré-requisitos: **Python 3.8+** (testado com 3.14.6) e **Docker com Compose**. Os
scripts usam só a biblioteca padrão do Python — não há nada para instalar.

**1. Configure o `.env`** (este arquivo não vai para o Git):

```powershell
Copy-Item .env.example .env
# edite POSTGRES_USER, POSTGRES_PASSWORD e POSTGRES_DB no seu .env
```

**2. Baixe a série do Banco Central e gere a carga:**

```powershell
python meu-loop-agente\workspace\scripts\baixar_dados.py
python meu-loop-agente\workspace\scripts\gerar_seed.py
```

O primeiro grava `data/raw/ipca_433.json` (561 meses, de 1980 a 2026) sem sobrescrever
um arquivo existente; o segundo escreve `meu-loop-agente/workspace/db/seed.sql`.

**3. Suba o banco e a API (juntos):**

```powershell
docker compose up -d --build
docker compose ps          # devem aparecer 2 containers: postgres (healthy) e api (healthy)
```

A primeira subida constrói a imagem da API, o que leva alguns minutos (instala as
dependências do `requirements.txt`).

**4. Carregue os dados.** O `init.sql` roda sozinho na primeira subida do container; o
seed é aplicado à mão (assim dá para recarregar quantas vezes quiser):

```powershell
Get-Content meu-loop-agente\workspace\db\seed.sql | docker compose exec -T postgres psql -U termometro -d termometro
```

**5. Confira** com as quatro consultas de `verificacao.sql`:

```powershell
Get-Content meu-loop-agente\workspace\db\verificacao.sql | docker compose exec -T postgres psql -U termometro -d termometro
```

**6. Teste os endpoints** (detalhes na seção [Endpoints](#endpoints)):

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/ipca/ultimo
curl "http://localhost:8000/ipca/serie?tipo=real"
```

**7. Veja o estado do loop:**

```powershell
python meu-loop-agente\verificar_iteracao.py estado
```

### Rodar a API sem Docker (banco na nuvem)

Quando o Docker não está disponível, o banco pode ficar no **Neon** (PostgreSQL
gerenciado, plano gratuito) e a API continua rodando na sua máquina.

**1. Tenha a URL de conexão no `.env`.** O comando `neon init` grava a variável sozinho;
se preferir, cole a connection string do console do Neon:

```
DATABASE_URL=postgresql://usuario:senha@host/banco?sslmode=require
AMBIENTE=neon
```

**2. Instale as dependências da API** (uma vez):

```powershell
pip install -r meu-loop-agente\workspace\api\requirements.txt
```

**3. Crie a tabela e carregue os dados no banco da nuvem:**

```powershell
python meu-loop-agente\workspace\scripts\aplicar_sql_nuvem.py
```

O script lê `init.sql` e `seed.sql` e envia pela `DATABASE_URL`. Ele usa a biblioteca
`psycopg2`; se ela não estiver instalada, cai no CLI do Neon (`neon psql`).

**4. Suba a API:**

```powershell
cd meu-loop-agente\workspace\api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**5. Teste:**

```powershell
curl http://localhost:8000/health
```

A resposta traz `"origem": "nuvem (DATABASE_URL)"`, provando de onde vêm os dados.

> O `instalar.py` faz esses quatro passos sozinho: escolha a opção `3` (ambiente **Neon**)
> e depois a `8` (instalar tudo).

## Endpoints

Base: `http://localhost:8000` (ou a porta definida em `API_PORT` no `.env`).

| Rota | O que devolve | Exemplo |
|---|---|---|
| `GET /health` | Prova de vida: pergunta a versão ao PostgreSQL antes de responder | `{"status":"ok","postgres":"ok","versao_postgres":"PostgreSQL 16.x ..."}` |
| `GET /ipca/ultimo` | O registro de maior data | `{"data":"2099-02-01","valor":2.3456,"tipo":"ficticio"}` |
| `GET /ipca/serie` | A série inteira, em ordem crescente de data | `[{"data":"1980-01-01","valor":6.62,"tipo":"real"}, ...]` |
| `GET /ipca/serie?tipo=real` | Só os meses reais; o filtro aceita `real` ou `ficticio` | idem, sem os dois de 2099 |

`/ipca/ultimo` devolve **2099-02-01** de propósito: os dois registros fictícios estão no
ano 2099 e são, por definição, os mais recentes. É o teste de que a ordenação funciona.

A documentação interativa do FastAPI (Swagger) fica em <http://localhost:8000/docs>.

### Alternativa opcional: MySQL

O projeto roda em PostgreSQL. Existe um **extra opcional** com MySQL 8, em arquivo
separado para não atropelar o banco principal:

```powershell
docker compose -f docker-compose.mysql.yml up -d
python meu-loop-agente\workspace\scripts\gerar_seed.py --dialeto mysql
```

O seed muda de dialeto porque o comando que ignora mês repetido tem nome diferente:
`ON CONFLICT (data) DO NOTHING` no PostgreSQL e `ON DUPLICATE KEY UPDATE` no MySQL.
A API **não** sobe com esse banco — ela lê do PostgreSQL.

## 🚀 Convite à interação

- **Iniciantes:** o primeiro PR pode ser pequeno — melhorar uma mensagem de erro, escrever
  um teste ou ajustar esta documentação. Eu reviso e explico o que mudou.
- **Colegas de programação:** abra uma Issue ou PR se encontrar gargalo, brecha de
  segurança ou uma modelagem melhor para a série do IPCA.
- **Recrutadores e visitantes:** é projeto real, construído em ciclos, com o log em
  [`meu-loop-agente/log.md`](meu-loop-agente/log.md) — não é tutorial copiado.

## Decisões técnicas

Cada decisão com alternativa considerada e consequência assumida fica em um **ADR**
(Architecture Decision Record — registro curto do porquê de uma escolha):

- [ADR 0001 — Por que PostgreSQL neste degrau](docs/adr/0001-por-que-postgresql.md):
  compara com SQLite, MySQL e CSV, e explica `NUMERIC(10,4)`, o `UNIQUE` em `data` e o
  índice `data DESC`.

As decisões de processo (o que ficou fora do degrau e por quê) estão em
[`docs/proximo-degrau.md`](docs/proximo-degrau.md).

## Limitações conhecidas

O que este projeto **não** faz — de propósito, por escopo do degrau:

- **Sem testes automatizados.** Toda verificação é manual (`curl`, consulta SQL). Um erro
  de regressão só aparece se alguém olhar; é exatamente o que o Degrau 2 resolve.
- **Sem CI/CD.** Nada roda sozinho a cada push; o gancho `pre-commit` e o `pre-push`
  impedem segredo, mas não testam código.
- **Sem autenticação.** Quem alcança a porta 8000 lê a série inteira. É API de leitura
  local, não serviço público.
- **API só de leitura.** Não há `POST`, `PUT` nem `DELETE`; a carga acontece pelo
  `seed.sql`, aplicado à mão.
- **Dados fictícios convivem com os reais.** Os dois registros de 2099 contaminam
  qualquer média ou contagem que não filtre `?tipo=real`.
- **Sem migração de schema.** Não há Alembic: mudar `init.sql` exige recriar o volume
  `pgdata` e reaplicar o seed.
- **Uma única série (433).** Não há comparação com outras séries, nem tratamento da
  mudança de metodologia do IPCA em 1999.

## Evidências

Saídas reais do programa, capturadas em 29/10/2026. As imagens são desenhadas a
partir do texto real (não são fotografias da tela) — a ressalva e o comando de cada uma
estão em [`docs/img/LOG-IMAGENS.md`](docs/img/LOG-IMAGENS.md).

![Menu do instalador com as 10 opções e o banco configurado](docs/img/01-menu-instalador.png)

*O menu do instalador: cada opção tem descrição, o banco atual aparece no cabeçalho e a
opção `0` encerra.*

![Erro do instalador quando o Docker não existe, com motivo e próximo passo](docs/img/12-sem-docker-condicionante.png)

*A condicionante do Docker: o fluxo para antes de tentar rodar comando impossível e diz o
motivo e o que fazer agora.*

As demais (`02-pre-requisitos.png`, `11-opcao-invalida.png` e `13-opcao-8-etapas.png`)
estão em [`docs/img/`](docs/img/), com a legenda no mesmo log.

![Opção 8 anunciando as 6 etapas e dizendo em qual parou](docs/img/13-opcao-8-etapas.png)

*A opção 8 (instalar tudo) numera as etapas e, ao falhar, diz onde parou, o que já deu
certo e que nada foi desfeito — em vez de voltar ao menu em silêncio.*

## Apoie o autor

- **PIX:** `a8b68e14-edfe-4450-88f2-c2af4aca2a6c`
- **Buy Me a Coffee:** <https://buymeacoffee.com/georgehbecker>
- **LinkedIn:** <https://www.linkedin.com/in/georgehbecker/>

## Topics sugeridos

```text
python sql postgresql docker ibge ipca dados-publicos loop-engineering
```