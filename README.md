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
API que consulta a série histórica do IPCA (SGS 433, Banco Central) armazenada em PostgreSQL rodando em Docker.

## Por que existe
É o Degrau 1 de uma trilha de 5 projetos pequenos que, juntos, formam as peças de um projeto final chamado "Encurtador de Links". Este degrau treina modelagem de banco relacional, Docker e seed.

## Onde esta técnica aparece no projeto final
No Encurtador, o PostgreSQL guarda os links e as campanhas; a modelagem aprendida aqui é a mesma usada lá.

## Como rodar
Em construção. Será preenchido nos Dias 2 e 3.

## Estrutura de pastas
- `.githooks/` — ganchos de proteção.
- `docs/` — documentos do projeto.
- `meu-loop-agente/` — contrato, config, baseline, log, verificador e system prompt.
- `workspace/` — código da aplicação (única pasta onde o agente atua).
- `data/raw/` — dados brutos do BCB.
- `data/processed/` — dados tratados.
## Como rodar

O verificador usa **somente a biblioteca padrão** do Python — não há dependência para
instalar ainda.

```powershell
python --version                          # testado com 3.14.6 (mínimo 3.8)
python meu-loop-agente\verificar_iteracao.py estado
```

Para abrir o projeto no VS Code:

```powershell
code --new-window D:\Projetos\ipca-postgres-docker
```

## 🚀 Convite à interação

- **Iniciantes:** o primeiro PR pode ser pequeno — melhorar uma mensagem de erro, escrever
  um teste ou ajustar esta documentação. Eu reviso e explico o que mudou.
- **Colegas de programação:** abra uma Issue ou PR se encontrar gargalo, brecha de
  segurança ou uma modelagem melhor para a série do IPCA.
- **Recrutadores e visitantes:** é projeto real, construído em ciclos, com o log em
  [`meu-loop-agente/log.md`](meu-loop-agente/log.md) — não é tutorial copiado.

## Transparência e limitações

- **Sem Docker ainda:** o `docker-compose` do PostgreSQL é o primeiro ciclo pendente; o
  Docker não está instalado na máquina onde a base foi criada, então nada foi testado.
- **Sem dados e sem schema:** nenhuma série do IPCA foi baixada, limpa ou carregada.
- **Contrato do loop no exemplo da base:** `program.md` e `config_loop.json` ainda falam
  do exemplo Next.js (métrica de bundle) e precisam da métrica real do projeto.
- **`.env` herdado da base:** o arquivo local aponta `DB_URL` para SQLite; a troca para
  PostgreSQL é decisão do dono do projeto.

## Apoie o autor

- **PIX:** `a8b68e14-edfe-4450-88f2-c2af4aca2a6c`
- **Buy Me a Coffee:** <https://buymeacoffee.com/georgehbecker>
- **LinkedIn:** <https://www.linkedin.com/in/georgehbecker/>

## Topics sugeridos

```text
python sql postgresql docker ibge ipca dados-publicos loop-engineering
```