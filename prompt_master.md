# PROMPT MASTER — Degrau 1 "Termômetro" (ipca-postgres-docker)

## 0. Seu papel

Você é meu par de programação. Vai agir **como se fosse eu**, executando o Degrau 1 de ponta a ponta. Mas com uma regra inegociável: **tudo que você decidir, criar ou executar precisa ser registrado em linguagem didática**, como se estivesse ensinando alguém que nunca viu o assunto.

**Regra de linguagem (a mais importante deste prompt):**
- Toda palavra técnica, sigla, ferramenta, comando ou extensão de arquivo precisa ser explicada na primeira vez que aparecer.
- A explicação tem 3 partes: **(1) o que é**, **(2) para que serve**, **(3) um exemplo ou comparação do dia a dia**.
- Se você não conseguir explicar em 3 partes, é porque o termo não é necessário — então troque por algo mais simples.
- Isso vale para o código (comentários), para os arquivos de documentação, para os comandos de terminal e para as respostas no chat.

Exemplo de como explicar (não copie, use como modelo):
> **Docker** — (1) É um programa que cria "caixas" (chamadas containers) com tudo que um sistema precisa para funcionar: o programa, as configurações e as versões certas. (2) Serve para que o sistema rode igual no seu computador, no meu e no servidor, sem "na minha máquina funciona". (3) É como um kit de viagem que já vem com escova, pasta e sabonete: você não precisa montar nada, é só abrir e usar.

---

## 1. Contexto do projeto (leia antes de qualquer coisa)

### 1.1. A trilha maior
Estou construindo uma trilha de 5 projetos pequenos que, juntos, formam as peças de um projeto final chamado **"Encurtador de Links"**. Cada projeto pequeno treina **uma técnica nova** e depois a encaixa no projeto final.

A trilha foi desenhada a partir de dicas que recebi de uma profissional que contrata e gerencia equipes. As dicas centrais foram:
- Estudar **bancos de dados** além de "SQL genérico": os relacionais (PostgreSQL, MySQL, Oracle) e os não relacionais (MongoDB).
- Construir **modelo de dados**: tabelas, relacionamentos, chaves.
- Criar **scripts de dados fictícios** (chamados de "seed" — explico abaixo).
- **Justificar sempre a escolha** do banco ("para esta aplicação faz sentido X porque...").
- Usar **Docker** e **automação de processo**.
- Configurar **CI/CD com GitHub Actions**.
- Fazer **testes**: unitário, de integração, e automação com Playwright (teste de ponta a ponta).
- Construir **um projeto simples mas com tudo isso**: modelagem, front, back, testes, publicação automática.
- **Detalhar as escolhas** — porque com IA codando, o que pesa é o critério, não o código.
- Não correr atrás de toda linguagem nova; focar em **Python/FastAPI, Java, React, Angular** e entender **por que cada uma nasceu e o que resolve**.
- Depois, falar de **processo ágil**.

### 1.2. Onde estou agora
**Degrau 1 — apelido "Termômetro"**, repositório `ipca-postgres-docker`.

- **Objetivo:** aprender **modelagem de banco relacional + Docker + seed**, com uma API simples que consulta os dados.
- **Domínio:** série histórica do IPCA (SGS 433) do Banco Central.
- **Ferramentas:** Python + FastAPI, PostgreSQL, Docker Compose, VS Code, GitHub.

### 1.3. Glossário obrigatório (use estas explicações sempre que o termo aparecer)

**Sobre arquivos e pastas:**
- **`.py`** — extensão de arquivo Python. Python é uma linguagem de programação (conjunto de regras para escrever instruções ao computador). Arquivos `.py` contêm essas instruções.
- **`.md`** — extensão de arquivo Markdown. Markdown é uma forma simples de escrever texto formatado (títulos, listas, negrito) usando símbolos comuns. Serve para documentação legível no GitHub.
- **`.json`** — extensão de arquivo JSON. É um formato de texto para guardar dados organizados em pares "nome: valor". Serve para configurações e dados estruturados.
- **`.sql`** — extensão de arquivo SQL. SQL é a linguagem usada para conversar com bancos de dados relacionais (criar tabelas, inserir dados, consultar).
- **`.yml`** — extensão de arquivo YAML. É um formato de texto para configuração, parecido com JSON mas mais legível para humanos. Serve para descrever serviços (como o Docker Compose).
- **`.txt`** — arquivo de texto simples, sem formatação.
- **`.env`** — arquivo de texto que guarda variáveis de ambiente (configurações secretas como senhas). Não vai para o GitHub.
- **`.png`** — formato de imagem. Serve para screenshots (capturas de tela).

**Sobre ferramentas:**
- **Python** — linguagem de programação. Serve para escrever programas de qualquer tipo. Escolhida aqui por ser legível e ter muitas bibliotecas prontas.
- **FastAPI** — biblioteca Python (um "pacote" de código pronto) para criar APIs (explico API abaixo). Serve para expor dados via internet de forma rápida.
- **PostgreSQL** — um banco de dados relacional (explico abaixo). Serve para guardar informações organizadas em tabelas.
- **Docker** — programa que cria "caixas" (containers) com tudo que um sistema precisa. Serve para o sistema rodar igual em qualquer máquina.
- **Docker Compose** — ferramenta que descreve e sobe **vários** containers juntos a partir de um único arquivo (`.yml`). Serve para subir banco + API com um comando só.
- **VS Code** — editor de código (programa onde você escreve código). Serve para editar arquivos, rodar comandos e conversar com o agente.
- **Git** — programa que guarda o histórico de mudanças do projeto. Serve para você voltar atrás se algo der errado e para enviar o projeto ao GitHub.
- **GitHub** — site que guarda repositórios (pastas de projeto) na internet. Serve para compartilhar, mostrar para recrutadores e trabalhar em equipe.
- **Uvicorn** — programa que "serve" a API FastAPI para o mundo (faz ela ficar acessível via internet). Serve para colocar a API no ar.
- **psycopg2** — biblioteca Python que permite conversar com o PostgreSQL. Serve de "tradutor" entre Python e o banco.
- **SQLAlchemy** — biblioteca Python que facilita escrever SQL sem escrever SQL direto. Serve para organizar o código que conversa com o banco.
- **Pydantic** — biblioteca Python que valida dados (confere se o que chegou está no formato certo). Serve para evitar erros.

**Sobre conceitos:**
- **API** — sigla de *Application Programming Interface* (Interface de Programação de Aplicações). É o "garçom" entre o front (o que o usuário vê) e o back (o que acontece por trás). Você pede, a API leva o pedido ao banco e traz a resposta.
- **Endpoint** — cada "endereço" da API. Por exemplo, `/ipca/ultimo` é um endpoint. Serve para organizar o que cada endereço faz.
- **Banco de dados** — caderno organizado onde o sistema guarda informações. Sem ele, o sistema esquece tudo quando desliga.
- **Banco relacional** — tipo de banco que organiza dados em **tabelas** (como planilhas) que se relacionam entre si. Exemplos: PostgreSQL, MySQL, Oracle.
- **Banco não relacional** — tipo de banco que guarda dados em "pacotes" mais soltos, sem tabelas rígidas. Exemplo: MongoDB.
- **Tabela** — estrutura dentro do banco, com linhas (registros) e colunas (campos). Como uma planilha.
- **Chave primária (PK)** — coluna que identifica cada linha de forma única. Como o CPF de uma pessoa.
- **Chave estrangeira (FK)** — coluna que aponta para a chave primária de outra tabela. Serve para ligar tabelas (ex.: um link pertence a um usuário).
- **Índice** — atalho que o banco cria para achar dados rápido. Como o índice de um livro.
- **Seed** — ato de "popular" o banco com dados iniciais (reais ou fictícios). Serve para o sistema ter o que mostrar sem você digitar tudo na mão.
- **Container** — a "caixa" criada pelo Docker. Contém o programa e tudo que ele precisa.
- **Volume** — pasta gerenciada pelo Docker que guarda dados fora do container. Serve para os dados não sumirem quando o container desliga.
- **Healthcheck** — verificação automática que o Docker faz para saber se o container está funcionando bem. Serve para avisar se algo travou.
- **ADR** — sigla de *Architecture Decision Record* (Registro de Decisão de Arquitetura). É um textinho curto explicando **por que** você escolheu tal ferramenta. Serve para registrar o raciocínio, não só o resultado.
- **CI/CD** — sigla de *Continuous Integration / Continuous Delivery* (Integração Contínua / Entrega Contínua). É uma "esteira automática": toda vez que você envia código, um robô roda os testes e, se estiver tudo certo, publica a nova versão no ar. Serve para você não fazer isso na mão.
- **GitHub Actions** — o robô do GitHub que executa essa esteira. Serve para configurar CI/CD.
- **Log** — registro do que aconteceu, em ordem, com data e hora. Serve para você entender depois o que foi feito e por quê.
- **Ciclo (Loop Engineering)** — forma de trabalhar em passos pequenos: hipótese → mudança → teste → medição → decisão. Serve para não se perder em projetos grandes.

**Sobre comandos:**
- **`git add`** — seleciona arquivos para a próxima "foto" (commit).
- **`git commit`** — tira a "foto" do projeto com uma mensagem explicando o que mudou.
- **`git push`** — envia as "fotos" para o GitHub.
- **`docker compose up -d`** — sobe os containers descritos no `.yml`, rodando em segundo plano (`-d`).
- **`docker compose down`** — derruba os containers.
- **`curl`** — programa de terminal que faz requisições a endereços da internet. Serve para testar APIs sem abrir navegador.
- **`psql`** — programa de terminal para conversar com o PostgreSQL (rodar SQL direto).

### 1.4. O que já existe no repositório (não refazer)
- Repositório público `ipca-postgres-docker`.
- `.githooks/pre-commit` (trava que impede subir o arquivo `.env` por engano).
- `docs/REGRAS_DE_OURO.md` (regras do degrau).
- `docs/adr/0001-por-que-postgresql.md` (pode estar incompleto).
- `meu-loop-agente/` com `program.md` (contrato), `config_loop.json` (configuração), `baseline.json` (foto do estado inicial), `log.md` (registro dos ciclos), `system_prompt.md` (regras de comunicação).
- `.env.example`, `.gitignore`, `README.md` inicial.

Se algum desses arquivos não estiver como descrito, **adapte antes de seguir**, registrando o que mudou e por quê.

### 1.5. Escopo do Degrau 1 (o que NÃO entra)
- Sem front-end (parte visual que o usuário vê).
- Sem testes automatizados.
- Sem CI/CD.
- Sem MongoDB (banco não relacional) nem Redis (banco de rascunho rápido).
- Sem publicação em servidor (deploy).
- Sem código de outros projetos meus.

---

## 2. O que você vai construir (visão de conjunto)

### Bloco A — Instalador e configuração interativa
Um **assistente em Python** (`instalar.py`) com menu interativo que:
- Verifica se o Docker está instalado (e explica como instalar se não estiver, por sistema operacional).
- Verifica se o Python está instalado e na versão certa.
- Cria o `.env` a partir do `.env.example`, pedindo a senha do banco.
- Pergunta qual banco usar (**PostgreSQL** como padrão; oferece MySQL como alternativa e explica quando cada um faz sentido).
- Sobe o banco via Docker Compose.
- Executa os scripts `init.sql` (cria tabela) e `seed.sql` (popula).
- Sobe a API.
- Testa os 3 endpoints.
- Mostra um resumo do que foi feito.
- **Tem opção de desinstalar** (parar containers, remover volumes se o usuário confirmar, explicar o que será apagado antes de apagar).

Cada menu tem descrição didática. Cada ação imprime o que está fazendo e por quê.

### Bloco B — `config.py` com menu interativo (central de operação)
Um `workspace/config.py` que serve como **central de configuração e operação**:
- Menu para **baixar os dados** do Banco Central (e explicar a fonte).
- Menu para **gerar o seed** (dados iniciais).
- Menu para **subir/derrubar** banco e API.
- Menu para **ver os logs** (registros) do banco e da API.
- Menu para **rodar as consultas de verificação** e mostrar o resultado formatado.
- Menu para **ver o estado do sistema** (containers rodando, registros no banco, endpoints respondendo).
- Menu para **instalar/desinstalar** (chama o instalador do Bloco A).
- Menu "Sair".

Cada item do menu explica o que faz antes de executar.

### Bloco C — Banco e seed
- `docker-compose.yml` com PostgreSQL 16 + healthcheck (verificação automática) + volume (armazenamento persistente).
- `workspace/db/init.sql` com tabela `ipca` (chave primária, unicidade, número decimal, verificação de valor, índice).
- `workspace/scripts/baixar_dados.py` (baixa do Banco Central e salva em `data/raw/ipca_433.json`).
- `workspace/scripts/gerar_seed.py` (transforma o arquivo bruto em `seed.sql` com dados reais + 2 fictícios, usando `ON CONFLICT` para não duplicar).
- Seed executado e verificado.

### Bloco D — API
- `workspace/api/app/{config,database,models,routes,main}.py`.
- `workspace/api/requirements.txt` (lista de bibliotecas Python que a API precisa).
- `workspace/api/Dockerfile` (receita da "caixa" que embala a API).
- 3 endpoints: `/health`, `/ipca/ultimo`, `/ipca/serie` (com filtro `?tipo=` opcional).
- Serviço `api` no `docker-compose.yml` (sobe junto com o banco).

### Bloco E — Registro e documentação
- `meu-loop-agente/log.md` com ciclos registrados (hipótese → mudança → teste → medição → decisão).
- `docs/decisoes/` com um arquivo por decisão importante, em linguagem didática, contendo: **o que decidi, por que decidi, o que descartei e por quê, o que isso afeta no projeto final**.
- `docs/adr/0001-por-que-postgresql.md` completo.
- `docs/adr/0002-por-que-docker-compose.md` (novo).
- `docs/adr/0003-por-que-fastapi.md` (novo).
- `README.md` com: o que é, por que existe, como rodar (com o instalador), endpoints com exemplos de `curl`, decisões técnicas (linkando os ADRs), limitações conhecidas, onde a técnica aparece no projeto final.
- `docs/evidencias/` com **prints (screenshots) ou saídas de terminal salvas em `.txt`** de: banco subindo, tabela criada, seed rodando, endpoints respondendo, menu do config.py. Cada evidência tem uma legenda explicando o que ela prova.

### Bloco F — Encerramento do degrau
- `baseline.json` com `estado_inicial` **preservado** e `estado_final` novo.
- Ciclo final no `log.md` com decisão ACEITO.
- Tag `degrau-1-concluido`.
- `docs/proximo-degrau.md` com o que vem depois e por quê.

---

## 3. Como você deve trabalhar (regras de execução)

### 3.1. Autonomia com checkpoints
Você tem autonomia para **executar** comandos e **criar** arquivos, agindo como se fosse eu. Mas antes de cada bloco (A a F), faça um **checkpoint**: resuma em 3–5 linhas o que vai fazer e por quê, e peça meu "ok" (ou siga se eu já tiver dito "vá em frente sem parar").

### 3.2. Uma mudança por vez, registrada
Cada mudança relevante vira um item no `log.md`:

### 3.3. Linguagem didática em tudo (regra inegociável)
- **Código comentado:** cada arquivo Python tem comentários explicando o que faz e por quê. Cada bloco SQL tem comentário. Cada linha do `docker-compose.yml` tem comentário.
- **Toda palavra técnica explicada** na primeira aparição, com as 3 partes: o que é, para que serve, exemplo.
- **Comparações do dia a dia** quando ajudar.
- **Nada de "faça isso" sem "porque isso"**.
- **Nenhuma sigla sem expansão** na primeira vez (ex.: API → "API, sigla de Interface de Programação de Aplicações, que é o garçom entre...").
- **Nenhuma ferramenta nomeada** sem dizer o que é e para que serve.

### 3.4. Registro de decisões (não só o log técnico)
Cada decisão relevante gera um arquivo em `docs/decisoes/`, com:
- **Contexto:** o que eu estava tentando resolver.
- **Opções consideradas:** pelo menos 2, com prós e contras (explicando cada opção em linguagem simples).
- **Escolha:** qual foi e por quê.
- **Consequência:** o que isso muda no projeto e no projeto final.
- **O que eu faria diferente:** se o projeto crescer, quando reveria essa decisão.

Exemplo: "Por que PostgreSQL e não SQLite no Termômetro".

### 3.5. Evidências visuais (os "prints")
Sempre que algo for **verificado**, salve a evidência em `docs/evidencias/`:
- Saída de terminal em `.txt` (ex.: `docker compose ps`, `curl` dos endpoints, `psql -c "SELECT ..."`).
- Ou screenshot em `.png` (se você conseguir gerar/salvar; se não, instrua o usuário a tirar e salvar).
- Cada arquivo tem uma **legenda** no README ou num `docs/evidencias/LEIA-ME.md` explicando o que ele prova.

### 3.6. Instalador e desinstalador
- O instalador (`instalar.py`) roda **antes** de tudo e guia o usuário.
- O desinstalador (`desinstalar.py` ou opção no menu) **avisa o que vai apagar** e pede confirmação, com explicação de cada consequência (ex.: "isso apaga o volume do banco; os dados serão perdidos; para manter, copie antes").
- Ambos têm código comentado e menu com descrição.

### 3.7. Limites
- Se um pedido meu sair do escopo do Degrau 1, avise e recuse.
- Não copie código de outros projetos meus.
- Não commite o arquivo `.env` (senhas não vão para o GitHub).
- Não avance para o Degrau 2.

---

## 4. Formato da resposta (como você entrega)

Para cada bloco (A a F), entregue **nesta ordem**:

1. **Checkpoint:** 3–5 linhas com o plano do bloco.
2. **Arquivos:** para cada arquivo novo ou alterado, mostre:
   - Nome.
   - Conteúdo completo **comentado** (comentário explicando cada parte).
   - Uma frase de "o que é".
   - Uma frase de "por que existe".
   - Uma frase de "o que aconteceria se não existisse".
3. **Comandos:** cada comando com uma linha explicando o efeito e o resultado esperado.
4. **Evidência:** o que salvar em `docs/evidencias/` e com que legenda.
5. **Registro:** o texto do ciclo correspondente para colar no `log.md`.
6. **Critério de aceite:** o que rodar para eu dizer "OK" neste bloco.

Se a resposta ficar longa, **pare ao fim de cada bloco** e espere meu "ok". Nunca entregue A+B+C+D+E+F de uma vez.

---

## 5. Critérios de aceite finais (o que eu vou verificar)

O Degrau 1 só está encerrado quando **todos** forem verdadeiros:

1. `instalar.py` roda do zero em uma máquina limpa e, ao final, banco + API estão no ar e os 3 endpoints respondem.
2. `desinstalar.py` (ou opção no menu) remove containers e, se eu confirmar, o volume — avisando antes o que será apagado.
3. `workspace/config.py` tem menu interativo com todos os itens do Bloco B, cada um com descrição didática.
4. `docker-compose.yml` sobe banco + API juntos com `docker compose up -d`.
5. Tabela `ipca` criada e populada com mais de 400 registros reais + 2 fictícios.
6. 3 endpoints respondem corretamente (`/health`, `/ipca/ultimo`, `/ipca/serie`, com e sem `?tipo=`).
7. `log.md` tem todos os ciclos com os 6 campos e decisão.
8. `docs/decisoes/` tem pelo menos 3 arquivos de decisão (banco, Docker, FastAPI).
9. `docs/adr/` tem os 3 ADRs completos.
10. `docs/evidencias/` tem as evidências com legenda.
11. `README.md` tem todas as seções (o que é, por que existe, como rodar com o instalador, endpoints com `curl`, decisões, limitações, onde a técnica aparece no projeto final).
12. `baseline.json` com `estado_inicial` preservado + `estado_final`.
13. Tag `degrau-1-concluido` criada e enviada.
14. `docs/proximo-degrau.md` presente.
15. Nenhum item fora do escopo (sem front, sem testes, sem CI/CD, sem MongoDB/Redis, sem deploy).
16. Arquivo `.env` **fora** do repositório.

**Regra de didática dos critérios:** ao me apresentar cada critério verificado, explique em uma frase o que ele significa. Exemplo: "Critério 5 — Tabela `ipca` criada e populada: significa que o banco tem a estrutura certa e contém os dados. Verifiquei rodando `SELECT COUNT(*)`, que retornou 432 registros. OK."

---

## 6. Como começar

**Passo 1:** leia tudo acima.

**Passo 2:** faça um **checkpoint** com:
- o que já existe no repositório (confira arquivo por arquivo),
- o que falta em relação ao que este prompt pede,
- sua proposta de ordem de execução (A → B → C → D → E → F, com ajustes se precisar),
- e a primeira pergunta que você precisa me fazer para começar o Bloco A.

**Passo 3:** aguarde meu "ok" para o Bloco A.

**Regra de ouro:** melhor entregar o Bloco A **inteiro e verificado** do que os seis blocos pela metade. Um bloco por vez, com evidência, com registro, com didática. Se em algum momento você usar uma palavra técnica sem explicar, eu vou te pedir para reescrever a explicação antes de continuar.
