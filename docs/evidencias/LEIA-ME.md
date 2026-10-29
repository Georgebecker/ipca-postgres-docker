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

A seção de capturas do projeto limita a **5 imagens por projeto** e proíbe exponenciar
dados pessoais. Este projeto é de terminal, sem interface gráfica: a saída em `.txt` prova
mais do que um print (dá para copiar, comparar e versionar sem ruído). Se um dia houver
tela, as regras de captura valem normalmente.
