# Evidências — o que cada arquivo prova

Uma evidência é a **prova de que algo aconteceu de verdade**, e não apenas a afirmação de
que aconteceu. Aqui a prova é a saída do terminal, salva em `.txt` com a legenda no topo
do próprio arquivo.

**Como ler:** cada arquivo começa com três linhas — o que ele prova, o comando que o
gerou e a entrada digitada. O resto é a saída, copiada sem edição.

## Evidências geradas

| Arquivo | O que prova | Comando que gerou |
|---|---|---|
| `01-menu-instalador.txt` | O assistente existe, lista as 10 opções e encerra limpo | `python instalar.py` (entrada `0`) |
| `02-pre-requisitos.txt` | A opção 1 confere Python, Docker e Compose — e, sem Docker, explica como instalar por sistema operacional | `python instalar.py` (entrada `1`, depois `0`) |
| `03-gerar-seed.txt` | O seed é montado a partir do dado real: 563 linhas (561 meses + 2 fictícios) | `python .../gerar_seed.py` |
| `04-gerar-seed-mysql.txt` | O mesmo seed no dialeto MySQL, terminando em `ON DUPLICATE KEY UPDATE` | `python .../gerar_seed.py --dialeto mysql` |
| `09-menu-config.txt` | A central de operação existe, com 9 opções descritivas, e encerra limpo | `python meu-loop-agente/workspace/config.py` (entrada `0`) |
| `10-estado-sem-docker.txt` | O menu **não quebra** sem Docker: avisa, diz o que não conseguiu consultar e segue | `python meu-loop-agente/workspace/config.py` (entrada `7`, depois `0`) |
| `11-opcao-invalida.txt` | Resposta inválida é explicada (o que foi recusado, o que é aceito, qual é o padrão) | `python instalar.py` (entrada `x`, depois `0`) |
| `12-sem-docker-condicionante.txt` | A condicionante do Docker mostra **condição + motivo + o que fazer agora** | `python instalar.py` (entrada `4`, depois `0`) |
| `13-opcao-8-etapas.txt` | A opção 8 anuncia etapas numeradas (1/6…6/6) e, ao falhar, diz onde parou e o que fazer | `python instalar.py` (entrada `8`, depois `0`) |
| `14-neon-setup.txt` | O Neon está autenticado, o projeto existe e o banco responde a uma query | `neon orgs list`, `neon projects list`, `neon psql` |
| `15-neon-tabela-populada.txt` | A tabela `ipca` foi criada e recebeu **563 linhas** (561 + 2), conferidas por 3 consultas | `neon psql` com `init.sql` e `seed.sql` |
| `16-neon-api-endpoints.txt` | A API local responde os 3 endpoints lendo o banco na nuvem (`origem: nuvem (DATABASE_URL)`) | `python instalar.py` (entrada `6`) |
| `17-testes-com-feedback.txt` | Cada endpoint aparece com comando, esperado, obtido e veredito — **4 de 4 passaram**, com os números conferidos (563 e 561) | `python instalar.py` (entrada `7`, depois `0`) |

Todas foram geradas na máquina de desenvolvimento, **sem Docker**, porque nenhuma delas
precisa de container.

## Pendentes de captura

Estas exigem Docker e **não foram simuladas** — inventar a saída seria pior do que não ter
prova. Quando o ambiente com Docker estiver disponível, rode os comandos e salve a saída
com o mesmo padrão de legenda:

| Arquivo a criar | O que vai provar | Comando |
|---|---|---|
| `05-containers.txt` | Banco e API sobem juntos e ficam `healthy` | `docker compose ps` |
| `06-tabela-populada.txt` | A tabela existe e tem 563 linhas (561 reais + 2 fictícios) | `docker compose exec -T postgres psql -U termometro -d termometro -c "SELECT tipo, COUNT(*) FROM ipca GROUP BY tipo;"` |
| `07-endpoints.txt` | Os 3 endpoints respondem 200, com e sem `?tipo=` | `python meu-loop-agente/workspace/scripts/medir_endpoints.py` |
| `08-desinstalacao.txt` | O desinstalador avisa o que será apagado antes de agir | `python instalar.py` (opção `9`) |

## Sobre imagens (`.png`)

As imagens ficam em [`docs/img/`](../img/), com a legenda de cada uma em
[`LOG-IMAGENS.md`](../img/LOG-IMAGENS.md). Elas são **desenhadas a partir da saída real**
do programa, capturada no terminal — não são fotografias da tela. O conteúdo é fiel; o
enquadramento é feito por código, porque os comandos rodam em segundo plano e não há
janela de terminal para fotografar no momento da execução.

Um print real da tela pode ser tirado a qualquer momento: o log traz a coluna **Como
reproduzir** com o comando e a entrada exata de cada caso.
