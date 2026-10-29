#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py — central de operacao do Termometro (Degrau 1).

(1) O que e: um menu de terminal para o dia a dia do projeto. Voce escolhe o
    numero e ele executa a tarefa, explicando antes o que vai fazer.
(2) Para que serve: evita decorar os comandos de Docker, de SQL e dos scripts
    Python. Em vez de lembrar "docker compose exec -T postgres psql -U ...",
    voce escolhe "6) Rodar as consultas de verificacao".
(3) Comparacao: e o painel do carro. O motor (banco, API, scripts) e o mesmo,
    mas voce nao precisa abrir o capo para saber se esta tudo bem.

Diferenca em relacao ao instalar.py (da raiz do projeto):
- o instalar.py faz a instalacao UMA vez: confere pre-requisitos, cria .env,
  sobe tudo pela primeira vez;
- este config.py opera SEMPRE: baixa dado novo, gera seed, sobe e derruba,
  mostra logs, roda as consultas e diz o estado atual.

Onde ele fica e por que: dentro de `workspace/`, como pedido no contrato do
degrau. Atencao a uma consequencia: `workspace/` e a pasta onde o agente de
Loop Engineering PODE atuar. Este arquivo nao e alvo de ciclo: mudar o menu
nao move a metrica do degrau (endpoints). Ele e ferramenta de operacao humana.

Regras deste arquivo:
- usa so biblioteca padrao (nada para instalar);
- reaproveita as funcoes do `instalar.py` (titulo, perguntar, rodar, ler_env)
  em vez de reescrever: se os dois divergissem, um deles passaria a mentir;
- cada opcao explica o que faz antes de fazer.

Uso:
    python meu-loop-agente/workspace/config.py
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

# Este arquivo vive em <raiz>/meu-loop-agente/workspace/config.py, entao subir
# duas pastas chega na raiz do projeto: workspace -> meu-loop-agente -> raiz.
RAIZ = Path(__file__).resolve().parents[2]

ARQ_INSTALADOR = RAIZ / "instalar.py"
SCRIPT_BAIXAR = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "baixar_dados.py"
SCRIPT_GERAR_SEED = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "gerar_seed.py"
SCRIPT_MEDIR = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "medir_endpoints.py"
ARQ_VERIFICACAO = RAIZ / "meu-loop-agente" / "workspace" / "db" / "verificacao.sql"
ARQ_RAW = RAIZ / "data" / "raw" / "ipca_433.json"


def carregar_auxiliar():
    """Carrega o `instalar.py` da raiz como modulo auxiliar.

    Por que assim: o arquivo esta fora desta pasta, e nao e um pacote Python
    instalado. O importlib permite importar pelo caminho do arquivo, sem
    mexer no sys.path (que poderia confundir outros imports do projeto).

    Levanta SystemExit com mensagem clara se o instalar.py nao existir — sem
    ele, nao teriamos as funcoes de leitura do .env e de execucao de comando.
    """
    if not ARQ_INSTALADOR.exists():
        print("[erro] nao encontrei o instalar.py na raiz do projeto.")
        print("       Ele tem as funcoes que este menu usa (ler o .env, rodar comando).")
        raise SystemExit(1)

    especificacao = importlib.util.spec_from_file_location("instalador", ARQ_INSTALADOR)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


# ---------------------------------------------------------------------------
# Opcao 1 — baixar os dados do Banco Central
# ---------------------------------------------------------------------------

def baixar_dados(aux) -> None:
    """Baixa (ou rebaixa) a serie 433 do Banco Central para data/raw/."""
    aux.titulo("Baixar os dados do Banco Central")
    aux.explicar(
        "Fonte: a API publica do Banco Central (SGS — Sistema Gerenciador de Series",
        "Temporais). A serie 433 e a variacao mensal do IPCA, de 1980 ate o ultimo",
        "mes fechado: hoje, 561 registros.",
        "",
        "O arquivo vai para data/raw/ipca_433.json e NAO e alterado depois: ele e a",
        "prova do que o Banco Central entregou naquele dia. Para refazer a carga, o",
        "seed.sql e regerado a partir dele (opcao 2).",
    )

    comando = [sys.executable, str(SCRIPT_BAIXAR)]
    if ARQ_RAW.exists():
        aux.aviso("ja existe um arquivo baixado em data/raw/.")
        aux.explicar(
            "  Baixar de novo substitui o arquivo atual. Use isso quando quiser",
            "  incluir o mes mais recente que o Banco Central publicou.",
        )
        if not aux.confirmar("Baixar de novo e sobrescrever o raw?", padrao_sim=False):
            aux.aviso("nada foi feito; o arquivo atual continua valendo.")
            return
        comando.append("--forcar")

    aux.rodar(comando, "baixar a serie 433 (20 kB, rapido)")


# ---------------------------------------------------------------------------
# Opcao 2 — gerar o seed
# ---------------------------------------------------------------------------

def gerar_seed(aux) -> None:
    """Transforma o raw em seed.sql, no dialeto do banco escolhido no .env."""
    banco = aux.banco_atual()
    aux.titulo("Gerar o seed.sql")
    aux.explicar(
        "O seed e o arquivo SQL que insere os dados no banco. Ele e gerado a partir",
        "do raw baixado na opcao 1, com duas linhas ficticias de 2099 no fim (para",
        "existir dado de teste que salta aos olhos).",
        "",
        "Dialeto atual: " + banco + ".",
        "  PostgreSQL usa ON CONFLICT (data) DO NOTHING;",
        "  MySQL usa ON DUPLICATE KEY UPDATE.",
        "Rodar o seed duas vezes nao duplica nada.",
    )
    if not ARQ_RAW.exists():
        aux.aviso("o raw ainda nao foi baixado; rode a opcao 1 primeiro.")
    aux.rodar(
        [sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", banco],
        "gerar seed.sql a partir do raw (dialeto " + banco + ")",
    )


# ---------------------------------------------------------------------------
# Opcao 3 — subir banco e API
# ---------------------------------------------------------------------------

def subir(aux) -> None:
    """Sobe banco e API com um comando."""
    banco = aux.banco_atual()
    aux.titulo("Subir banco e API")
    aux.explicar(
        "O Docker Compose le o docker-compose.yml e sobe os dois containers.",
        "-d significa 'em segundo plano': o terminal volta para voce.",
        "--build refaz a imagem da API se o codigo mudou (na primeira vez, sempre).",
        "",
        "A API so sobe depois que o banco responde ao healthcheck (depends_on).",
    )
    if banco == "mysql":
        aux.aviso("BANCO=mysql: o docker-compose.yml padrao sobe PostgreSQL.")
        aux.explicar(
            "  Para o extra de MySQL use: docker compose -f docker-compose.mysql.yml up -d",
            "  A API deste projeto le do PostgreSQL, entao ela nao sobe junto.",
        )
        return
    aux.rodar(["docker", "compose", "up", "-d", "--build"],
              "subir banco e API em segundo plano")


# ---------------------------------------------------------------------------
# Opcao 4 — derrubar
# ---------------------------------------------------------------------------

def derrubar(aux) -> None:
    """Para e remove os containers (os dados continuam no volume)."""
    aux.titulo("Derrubar os containers")
    aux.explicar(
        "Isto para e remove os containers. NAO apaga os dados: eles moram no volume",
        "pgdata, que continua no disco. Quando voce subir de novo, o banco volta",
        "exatamente como estava.",
        "",
        "Para apagar os dados tambem, use a opcao 9 (desinstalar) do instalar.py.",
    )
    if not aux.confirmar("Parar os containers agora?", padrao_sim=True):
        aux.aviso("nada foi feito.")
        return
    aux.rodar(["docker", "compose", "down"], "parar e remover os containers")


# ---------------------------------------------------------------------------
# Opcao 5 — logs
# ---------------------------------------------------------------------------

def ver_logs(aux) -> None:
    """Mostra as ultimas linhas de log do banco e/ou da API."""
    aux.titulo("Ver os logs")
    aux.explicar(
        "Log e o diario do programa: tudo que ele escreveu enquanto rodava.",
        "E o primeiro lugar a olhar quando algo nao responde ou responde errado.",
        "",
        "Vou mostrar as ultimas 30 linhas de cada servico escolhido.",
    )
    escolha = aux.perguntar("Qual? 1 = banco, 2 = API, 3 = os dois", "3")
    servicos = {"1": ["postgres"], "2": ["api"], "3": ["postgres", "api"]}.get(
        escolha.strip(), ["postgres", "api"]
    )
    for servico in servicos:
        aux.rodar(["docker", "compose", "logs", "--tail=30", servico],
                  "ultimas 30 linhas do log do servico " + servico)


# ---------------------------------------------------------------------------
# Opcao 6 — consultas de verificacao
# ---------------------------------------------------------------------------

def consultas(aux) -> None:
    """Roda as 4 consultas de verificacao dentro do container do banco."""
    aux.titulo("Consultas de verificacao")
    aux.explicar(
        "Sao quatro perguntas objetivas ao banco (arquivo db/verificacao.sql):",
        "  1) quantas linhas existem na tabela ipca;",
        "  2) quantas sao reais e quantas sao ficticias;",
        "  3) quais sao os cinco meses mais recentes;",
        "  4) quais indices existem na tabela.",
        "",
        "Cada consulta traz no comentario o resultado esperado. Se um numero nao",
        "bater, o banco nao esta com os dados do seed.",
    )
    if not ARQ_VERIFICACAO.exists():
        aux.erro("nao encontrei o arquivo " + str(ARQ_VERIFICACAO.relative_to(RAIZ)) + ".")
        return

    if aux.banco_atual() == "mysql":
        aux.aviso("as consultas deste arquivo estao em dialeto PostgreSQL.")
        aux.explicar("  Com BANCO=mysql, use o cliente do MySQL para conferir manualmente.")
        return

    config = aux.ler_env()
    comando = ["docker", "compose", "exec", "-T", "postgres", "psql",
               "-U", config.get("POSTGRES_USER", "termometro"),
               "-d", config.get("POSTGRES_DB", "termometro")]
    aux.rodar(comando, "rodar as 4 consultas de verificacao",
              entrada=ARQ_VERIFICACAO.read_bytes())


# ---------------------------------------------------------------------------
# Opcao 7 — estado do sistema
# ---------------------------------------------------------------------------

def contar_registros(aux) -> str:
    """Pergunta ao banco quantas linhas existem; devolve o numero ou uma explicacao."""
    config = aux.ler_env()
    try:
        resultado = subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "psql",
             "-U", config.get("POSTGRES_USER", "termometro"),
             "-d", config.get("POSTGRES_DB", "termometro"),
             "-t", "-A", "-c", "SELECT COUNT(*) FROM ipca;"],
            cwd=str(RAIZ),
            capture_output=True,
            timeout=60,
        )
    except (subprocess.TimeoutExpired, OSError):
        return "nao foi possivel consultar"
    if resultado.returncode != 0:
        # O caso mais comum: o container nao esta rodando ou a tabela nao existe.
        return "banco fora do ar ou tabela ausente"
    return (resultado.stdout or b"").decode("utf-8", "replace").strip() or "sem resposta"


def estado(aux) -> None:
    """Mostra o retrato do sistema: containers, linhas no banco e endpoints."""
    aux.titulo("Estado do sistema")
    aux.explicar(
        "Tres perguntas, na ordem em que costumam falhar:",
        "  1) os containers estao de pe? (docker compose ps)",
        "  2) o banco tem os dados? (SELECT COUNT(*) FROM ipca)",
        "  3) a API responde? (chamada nos 3 endpoints)",
    )

    aux.rodar(["docker", "compose", "ps"], "listar os containers do projeto")

    print("")
    print("  # perguntar ao banco quantas linhas existem")
    total = contar_registros(aux)
    if total.isdigit():
        aux.ok("tabela ipca com " + total + " linhas (esperado: 563 = 561 reais + 2 ficticios)")
    else:
        aux.aviso("contagem indisponivel: " + total)

    print("")
    print("  # testar os 3 endpoints")
    aux.rodar([sys.executable, str(SCRIPT_MEDIR)], "medir quantos endpoints respondem")


# ---------------------------------------------------------------------------
# Opcoes 8 e 9 — instalar e desinstalar (delegam ao instalar.py)
# ---------------------------------------------------------------------------

def abrir_instalador(aux) -> None:
    """Abre o menu do instalar.py, que tem a instalacao e a desinstalacao.

    Por que delegar: a instalacao (criar .env, escolher banco, esperar o
    healthcheck) ja esta escrita e testada la. Reescrever aqui criaria duas
    versoes da mesma regra — e a que ninguem usa envelhece errado.
    """
    aux.titulo("Instalar / desinstalar")
    aux.explicar(
        "Vou abrir o menu do instalar.py. Nele:",
        "  opcao 8 -> instalar tudo na ordem;",
        "  opcao 9 -> desinstalar (avisa o que apaga e pede confirmacao).",
        "",
        "Ao sair do instalador, voce volta para este menu.",
    )
    try:
        subprocess.run([sys.executable, str(ARQ_INSTALADOR)], cwd=str(RAIZ))
    except OSError as falha:
        aux.erro("nao consegui abrir o instalar.py: " + str(falha))


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

OPCOES = [
    ("1", "Baixar os dados do Banco Central (serie 433)"),
    ("2", "Gerar o seed.sql a partir do dado baixado"),
    ("3", "Subir banco e API"),
    ("4", "Derrubar os containers (os dados ficam no volume)"),
    ("5", "Ver os logs (banco e/ou API)"),
    ("6", "Rodar as consultas de verificacao"),
    ("7", "Ver o estado do sistema (containers, linhas, endpoints)"),
    ("8", "Instalar ou desinstalar (abre o instalar.py)"),
    ("0", "Sair"),
]


def mostrar_menu(aux) -> None:
    """Desenha o menu com a situacao atual do banco configurado."""
    aux.titulo("Termometro — central de operacao")
    aux.explicar(
        "Escolha o numero. Cada opcao explica o que faz antes de agir.",
        "Banco configurado: " + aux.banco_atual(),
    )
    print("")
    for numero, descricao in OPCOES:
        print("  " + numero + ") " + descricao)


def main() -> int:
    """Loop do menu. Devolve 0 ao sair normalmente."""
    aux = carregar_auxiliar()

    acoes = {
        "1": baixar_dados,
        "2": gerar_seed,
        "3": subir,
        "4": derrubar,
        "5": ver_logs,
        "6": consultas,
        "7": estado,
        "8": abrir_instalador,
    }

    while True:
        mostrar_menu(aux)
        escolha = aux.perguntar("Opcao", "0").strip()

        if escolha == "0":
            print("")
            print("  Ate logo. Para voltar: python meu-loop-agente/workspace/config.py")
            return 0

        acao = acoes.get(escolha)
        if acao is None:
            aux.aviso("opcao invalida; escolha um numero do menu.")
            continue
        acao(aux)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("")
        print("  interrompido pelo usuario. Nada foi desfeito.")
        sys.exit(130)
