#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""instalar.py — assistente de instalacao do projeto Termometro.

(1) O que e: um programa de terminal que conduz a instalacao passo a passo,
    num menu. Voce escolhe o numero e ele executa.
(2) Para que serve: evita decorar comandos de Docker, de SQL e de Python, e
    evita esquecer uma etapa (subir o banco sem carregar os dados, por exemplo).
(3) Comparacao: e o "assistente de embarque" do aeroporto. Voce ainda faz a
    viagem, mas alguem te diz a ordem certa dos passos e confere o bilhete.

Regras deste arquivo:
- usa SO a biblioteca padrao do Python (nada para instalar antes);
- cada acao imprime o que vai fazer e por que, antes de fazer;
- nada de senha no codigo: ela e pedida na hora e gravada no `.env`.

Uso:
    python instalar.py

Observacao sobre acentos: no console antigo do Windows (pagina de codigo 850)
os acentos podem aparecer como "?". O arquivo esta correto em UTF-8; use o
Windows Terminal ou o terminal do VS Code para ver tudo.
"""

import getpass
import json
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ARQ_ENV = RAIZ / ".env"
ARQ_ENV_EXEMPLO = RAIZ / ".env.example"
ARQ_SEED = RAIZ / "meu-loop-agente" / "workspace" / "db" / "seed.sql"
SCRIPT_GERAR_SEED = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "gerar_seed.py"
ARQ_COMPOSE_MYSQL = RAIZ / "docker-compose.mysql.yml"

URL_API = "http://localhost:8000"
CONTAINER_POSTGRES = "termometro-postgres"
CONTAINER_MYSQL = "termometro-mysql"

# Tempo maximo esperando o banco ficar "healthy" (pronto para receber conexao).
LIMITE_ESPERA_SEGUNDOS = 60


# ---------------------------------------------------------------------------
# Mensagens na tela
# ---------------------------------------------------------------------------

def titulo(texto: str) -> None:
    """Imprime um cabecalho, para separar uma secao da outra."""
    print("")
    print("=" * 64)
    print(texto)
    print("=" * 64)


def explicar(*linhas: str) -> None:
    """Mostra a explicacao didatica de uma acao antes de executa-la."""
    for linha in linhas:
        print("  " + linha)


def ok(mensagem: str) -> None:
    print("  [ok] " + mensagem)


def aviso(mensagem: str) -> None:
    print("  [aviso] " + mensagem)


def erro(mensagem: str) -> None:
    print("  [erro] " + mensagem)


def perguntar(pergunta: str, padrao: str = "") -> str:
    """Le uma resposta do teclado. Enter vazio devolve o padrao."""
    sufixo = " [" + padrao + "]" if padrao else ""
    resposta = input("  " + pergunta + sufixo + ": ").strip()
    return resposta or padrao


def confirmar(pergunta: str, padrao_sim: bool = False) -> bool:
    """Pergunta sim/nao. Qualquer coisa diferente de 's' conta como nao."""
    padrao = "s" if padrao_sim else "n"
    return perguntar(pergunta + " (s/n)", padrao).lower().startswith("s")


# ---------------------------------------------------------------------------
# Execucao de comandos
# ---------------------------------------------------------------------------

def rodar(comando: list, motivo: str, entrada: bytes = None) -> tuple:
    """Executa um comando na raiz do projeto e devolve (deu_certo, saida).

    `motivo` e impresso antes, para que o usuario saiba por que aquele comando
    esta sendo rodado (o programa ensina enquanto trabalha).
    """
    print("")
    print("  # " + motivo)
    print("  $ " + " ".join(comando))
    try:
        resultado = subprocess.run(
            comando,
            cwd=str(RAIZ),
            input=entrada,
            capture_output=True,
            timeout=600,
        )
    except FileNotFoundError:
        erro("nao encontrei o programa '" + comando[0] + "' no PATH.")
        return False, ""
    except subprocess.TimeoutExpired:
        erro("o comando passou de 10 minutos e foi interrompido.")
        return False, ""

    saida = (resultado.stdout or b"").decode("utf-8", "replace")
    erros = (resultado.stderr or b"").decode("utf-8", "replace")
    texto = (saida + "\n" + erros).strip()
    if resultado.returncode != 0:
        erro("terminou com codigo " + str(resultado.returncode) + ".")
        for linha in texto.splitlines()[-8:]:
            print("       " + linha)
        return False, texto
    return True, texto


# ---------------------------------------------------------------------------
# .env — o caderno de configuracoes locais
# ---------------------------------------------------------------------------

def ler_env() -> dict:
    """Le o `.env` e devolve um dicionario chave -> valor.

    Linhas comecando com '#' e linhas vazias sao ignoradas. Se o arquivo nao
    existe, devolve dicionario vazio (quem chama decide o que fazer).
    """
    dados = {}
    if not ARQ_ENV.exists():
        return dados
    for linha in ARQ_ENV.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        dados[chave.strip()] = valor.strip()
    return dados


def definir_no_env(chave: str, valor: str) -> None:
    """Grava (ou substitui) uma chave no `.env`, preservando o resto do arquivo.

    Substituir "no lugar" e melhor que reescrever tudo: os comentarios que o
    dono escreveu no arquivo continuam onde estavam.
    """
    if not ARQ_ENV.exists():
        ARQ_ENV.write_text("", encoding="utf-8")
    linhas = ARQ_ENV.read_text(encoding="utf-8").splitlines()
    nova = chave + "=" + valor
    for indice, linha in enumerate(linhas):
        if linha.strip().startswith(chave + "="):
            linhas[indice] = nova
            break
    else:
        linhas.append(nova)
    ARQ_ENV.write_text("\n".join(linhas).rstrip("\n") + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Pre-requisitos
# ---------------------------------------------------------------------------

def instrucoes_de_instalacao_do_docker() -> None:
    """Explica como instalar o Docker no sistema do usuario."""
    sistema = platform.system()
    explicar(
        "O Docker e o programa que cria os containers (as 'caixas' com o banco",
        "e com a API dentro). Sem ele, nada sobe por este instalador.",
        "",
        "Como instalar no seu sistema (" + sistema + "):",
    )
    if sistema == "Windows":
        explicar(
            "  Windows: baixe o 'Docker Desktop' em https://docs.docker.com/desktop/",
            "  Depois de instalar, ABRA o Docker Desktop e espere o icone ficar verde.",
            "  Reinicie o terminal para o comando 'docker' aparecer.",
        )
    elif sistema == "Darwin":
        explicar(
            "  macOS: baixe o 'Docker Desktop' em https://docs.docker.com/desktop/mac/",
            "  Abra o app e espere ele terminar de iniciar.",
        )
    else:
        explicar(
            "  Linux: instale o 'docker' e o 'docker-compose-plugin' pelo gerenciador",
            "  de pacotes da sua distribuicao. Exemplo (Ubuntu):",
            "    sudo apt update && sudo apt install docker.io docker-compose-v2",
            "  Depois adicione seu usuario ao grupo docker:",
            "    sudo usermod -aG docker $USER   (e saia e entre na sessao de novo)",
        )
    explicar(
        "",
        "Depois de instalar, rode este instalador de novo.",
    )


def verificar_pre_requisitos() -> bool:
    """Confere Python, Docker e Docker Compose. Devolve True se tudo existe."""
    titulo("Verificacao dos pre-requisitos")
    explicar(
        "Vou conferir tres coisas antes de qualquer instalacao:",
        "  1) a versao do Python (o projeto precisa de 3.8 ou mais novo);",
        "  2) se o Docker esta instalado (ele roda o banco e a API);",
        "  3) se o comando 'docker compose' responde (e ele que le o .yml).",
    )

    tudo_certo = True

    versao = sys.version_info
    if versao >= (3, 8):
        ok("Python " + platform.python_version() + " (minimo 3.8)")
    else:
        erro("Python " + platform.python_version() + " e antigo; instale 3.8 ou mais novo.")
        tudo_certo = False

    if shutil.which("docker") is None:
        erro("o comando 'docker' nao foi encontrado.")
        instrucoes_de_instalacao_do_docker()
        return False
    ok("Docker encontrado")

    certo, _ = rodar(["docker", "compose", "version"], "Conferir se o Docker Compose responde")
    if certo:
        ok("Docker Compose responde")
    else:
        erro("o 'docker compose' nao respondeu.")
        explicar(
            "  Isso costuma significar uma de duas coisas:",
            "  - o Docker Desktop ainda esta iniciando (espere o icone ficar verde);",
            "  - a versao do Docker e antiga e nao tem o subcomando 'compose'.",
        )
        tudo_certo = False

    return tudo_certo


# ---------------------------------------------------------------------------
# 2. Arquivo .env
# ---------------------------------------------------------------------------

def criar_env() -> bool:
    """Cria o `.env` a partir do `.env.example` e pergunta a senha do banco."""
    titulo("Configuracao do arquivo .env")
    explicar(
        "O '.env' e um arquivo de texto com as configuracoes locais: nome do banco,",
        "usuario, porta e SENHA. Ele fica so na sua maquina e nunca vai para o GitHub",
        "(o .gitignore e o gancho pre-commit impedem isso).",
        "",
        "O modelo dele e o '.env.example', que tem as mesmas chaves mas com valores",
        "de mentira. Agora vou copiar o modelo e trocar a senha pela sua.",
    )

    if ARQ_ENV.exists() and not confirmar(".env ja existe. Recriar do zero?", padrao_sim=False):
        aviso("mantive o .env atual.")
        return True

    if not ARQ_ENV_EXEMPLO.exists():
        erro("nao encontrei o .env.example; sem ele nao sei quais chaves existem.")
        return False

    shutil.copyfile(str(ARQ_ENV_EXEMPLO), str(ARQ_ENV))
    ok(".env criado a partir do .env.example")

    senha = getpass.getpass("  Digite a senha do banco (nao aparece na tela): ").strip()
    if not senha:
        aviso("senha vazia; mantive o marcador 'troque_esta_senha'.")
    else:
        definir_no_env("POSTGRES_PASSWORD", senha)
        definir_no_env("MYSQL_ROOT_PASSWORD", senha)
        ok("senha gravada no .env (PostgreSQL e MySQL)")

    explicar(
        "",
        "Lembrete: o .env nunca deve ser commitado. Se algum dia aparecer um",
        "'.env' no 'git status' como novo arquivo, algo esta errado.",
    )
    return True


# ---------------------------------------------------------------------------
# 3. Escolha do banco
# ---------------------------------------------------------------------------

def escolher_banco() -> str:
    """Pergunta qual banco usar e grava a escolha no `.env`. Devolve o nome."""
    titulo("Escolha do banco de dados")
    explicar(
        "PostgreSQL (padrao do projeto):",
        "  - e o banco que a trilha usa; ja tem tabela, seed e API prontos;",
        "  - tipos exatos como NUMERIC(10,4) e CHECK funcionando sem surpresa.",
        "",
        "MySQL (extra opcional, experimental):",
        "  - serve para comparar os dois bancos e ver as diferencas de SQL;",
        "  - o seed precisa ser gerado com '--dialeto mysql';",
        "  - a API deste projeto le do PostgreSQL, entao com MySQL ela nao sobe.",
        "",
        "Para o Degrau 1, o caminho recomendado e o 1 (PostgreSQL).",
    )
    escolha = perguntar("Qual banco? 1 = PostgreSQL, 2 = MySQL", "1")
    banco = "mysql" if escolha.strip() == "2" else "postgres"
    definir_no_env("BANCO", banco)
    ok("banco escolhido: " + banco + " (gravado no .env como BANCO)")
    return banco


def banco_atual() -> str:
    """Le do `.env` qual banco foi escolhido; padrao postgres."""
    return ler_env().get("BANCO", "postgres").lower()


# ---------------------------------------------------------------------------
# 4. Subir o banco
# ---------------------------------------------------------------------------

def comando_compose(banco: str) -> list:
    """Monta o comando do Docker Compose certo para o banco escolhido."""
    if banco == "mysql":
        return ["docker", "compose", "-f", "docker-compose.mysql.yml"]
    return ["docker", "compose"]


def esperar_banco(banco: str) -> bool:
    """Espera o banco responder ao healthcheck, ate o limite de tempo.

    O healthcheck e uma verificacao automatica que o Docker faz de tempos em
    tempos. Enquanto ele nao diz 'healthy', o banco ainda esta acordando e
    qualquer conexao seria recusada.
    """
    container = CONTAINER_MYSQL if banco == "mysql" else CONTAINER_POSTGRES
    print("")
    print("  # Esperando o banco ficar pronto (healthcheck)...")
    limite = time.time() + LIMITE_ESPERA_SEGUNDOS
    while time.time() < limite:
        try:
            resultado = subprocess.run(
                ["docker", "inspect", "--format={{.State.Health.Status}}", container],
                capture_output=True,
                text=True,
                timeout=20,
            )
            estado = (resultado.stdout or "").strip()
        except (subprocess.TimeoutExpired, OSError):
            estado = ""
        if estado == "healthy":
            ok("o container " + container + " esta healthy")
            return True
        print("       estado atual: " + (estado or "desconhecido") + " ...")
        time.sleep(3)
    erro("o banco nao ficou pronto em " + str(LIMITE_ESPERA_SEGUNDOS) + " segundos.")
    explicar(
        "  Veja o que aconteceu com:",
        "    docker compose logs " + ("mysql" if banco == "mysql" else "postgres"),
    )
    return False


def subir_banco(banco: str = None) -> bool:
    """Sobe o container do banco escolhido."""
    banco = banco or banco_atual()
    titulo("Subindo o banco (" + banco + ")")
    explicar(
        "Vou pedir ao Docker Compose para criar e iniciar o container do banco.",
        "Na primeira vez ele baixa a imagem (pode demorar alguns minutos).",
        "O 'init.sql' roda sozinho nesta primeira subida, criando a tabela ipca.",
    )
    certo, _ = rodar(comando_compose(banco) + ["up", "-d", banco],
                     "subir o container do banco em segundo plano (-d)")
    if not certo:
        return False
    return esperar_banco(banco)


# ---------------------------------------------------------------------------
# 5. Estrutura + seed
# ---------------------------------------------------------------------------

def aplicar_sql(banco: str, arquivo: Path, motivo: str) -> bool:
    """Envia um arquivo .sql para dentro do container do banco.

    O arquivo e lido aqui e passado pela entrada padrao, em vez de depender de
    redirecionamento do shell. Assim funciona igual no PowerShell, no cmd e
    no bash.
    """
    if not arquivo.exists():
        erro("nao encontrei " + str(arquivo.relative_to(RAIZ)) + ".")
        return False
    conteudo = arquivo.read_bytes()
    config = ler_env()

    if banco == "mysql":
        comando = comando_compose("mysql") + [
            "exec", "-T", "-e", "MYSQL_PWD=" + config.get("MYSQL_ROOT_PASSWORD", ""),
            "mysql", "mysql", "-u", "root", config.get("MYSQL_DATABASE", "termometro"),
        ]
    else:
        comando = comando_compose("postgres") + [
            "exec", "-T", "postgres", "psql",
            "-U", config.get("POSTGRES_USER", "termometro"),
            "-d", config.get("POSTGRES_DB", "termometro"),
        ]
    return rodar(comando, motivo, entrada=conteudo)[0]


def carregar_dados(banco: str = None) -> bool:
    """Aplica a estrutura (init) e depois o seed."""
    banco = banco or banco_atual()
    titulo("Criando a tabela e carregando os dados")
    explicar(
        "Duas etapas:",
        "  1) init.sql  -> cria a tabela ipca (PK, UNIQUE em data, NUMERIC, CHECK, indice);",
        "  2) seed.sql  -> insere os 561 meses reais + 2 ficticios de 2099.",
        "",
        "Reaplicar os dois e seguro: a criacao usa IF NOT EXISTS e a insercao ignora",
        "mes que ja existe. Nada duplica.",
    )

    pasta = "mysql" if banco == "mysql" else ""
    inicial = RAIZ / "meu-loop-agente" / "workspace" / "db" / pasta / "init.sql"
    if not aplicar_sql(banco, inicial, "criar a tabela ipca (idempotente)"):
        return False

    # O seed precisa existir no dialeto certo. Se nao existir, gero agora.
    if not ARQ_SEED.exists():
        aviso("seed.sql nao existe; vou gerar a partir do raw.")
        if not (RAIZ / "data" / "raw" / "ipca_433.json").exists():
            explicar(
                "  O raw ainda nao foi baixado. Rodando o download agora...",
            )
            rodar([sys.executable, "meu-loop-agente/workspace/scripts/baixar_dados.py"],
                  "baixar a serie 433 do Banco Central")
        rodar([sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", banco],
              "gerar o seed.sql (dialeto " + banco + ")")

    # Se o seed foi gerado para outro dialeto, regenera: o comando de "nao
    # duplicar" e diferente em cada banco.
    cabecalho = ARQ_SEED.read_text(encoding="utf-8", errors="replace")[:300]
    if ("Dialeto: " + banco) not in cabecalho:
        aviso("o seed.sql esta em outro dialeto; regenerando para " + banco + ".")
        rodar([sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", banco],
              "regenerar o seed.sql no dialeto certo")

    if not aplicar_sql(banco, ARQ_SEED, "inserir os dados (ignora o que ja existe)"):
        return False

    ok("tabela criada e dados carregados")
    return True


# ---------------------------------------------------------------------------
# 6. API
# ---------------------------------------------------------------------------

def subir_api() -> bool:
    """Constroi e sobe o container da API (somente com PostgreSQL)."""
    titulo("Subindo a API")
    if banco_atual() == "mysql":
        aviso("a API deste projeto le do PostgreSQL. Com BANCO=mysql ela nao sobe.")
        explicar(
            "  Isso e de proposito: o extra de MySQL serve para estudar o banco,",
            "  nao para rodar o projeto inteiro. Volte com a opcao 3 (escolher banco)",
            "  e selecione PostgreSQL para subir a API.",
        )
        return False

    explicar(
        "Vou construir a imagem da API (instala FastAPI, Uvicorn e psycopg2 dentro",
        "de um container) e subir junto com o banco. A primeira construcao demora",
        "alguns minutos; as seguintes reaproveitam as camadas ja baixadas.",
    )
    certo, _ = rodar(["docker", "compose", "up", "-d", "--build", "api"],
                     "construir a imagem e subir a API")
    if not certo:
        return False
    ok("API no ar em " + URL_API)
    return True


# ---------------------------------------------------------------------------
# 7. Teste dos endpoints
# ---------------------------------------------------------------------------

def testar_endpoints() -> bool:
    """Faz uma chamada em cada um dos 3 endpoints e mostra o que voltou."""
    titulo("Testando os 3 endpoints")
    explicar(
        "Cada endpoint e um 'endereco' da API. Vou chamar os tres e mostrar o",
        "status HTTP (200 = deu certo) e os primeiros caracteres da resposta.",
    )
    caminhos = ["/health", "/ipca/ultimo", "/ipca/serie?tipo=real"]
    aprovados = 0
    for caminho in caminhos:
        url = URL_API + caminho
        try:
            with urllib.request.urlopen(url, timeout=10) as resposta:
                corpo = resposta.read().decode("utf-8", "replace")
                status = resposta.status
        except urllib.error.HTTPError as falha:
            erro(caminho + " -> HTTP " + str(falha.code))
            continue
        except urllib.error.URLError:
            erro(caminho + " -> sem conexao (a API esta no ar?)")
            continue

        if status == 200:
            aprovados += 1
            ok(caminho + " -> 200 | " + corpo[:90] + ("..." if len(corpo) > 90 else ""))
        else:
            erro(caminho + " -> HTTP " + str(status))

    print("")
    print("  endpoints respondendo: " + str(aprovados) + " de " + str(len(caminhos)))
    if aprovados == len(caminhos):
        explicar("  Todos responderam. O degrau esta verificavel de ponta a ponta.")
    else:
        explicar(
            "  Se algum falhou, veja o log da API:",
            "    docker compose logs api",
        )
    return aprovados == len(caminhos)


# ---------------------------------------------------------------------------
# 8. Instalacao completa
# ---------------------------------------------------------------------------

def instalar_tudo() -> None:
    """Roda a sequencia inteira: .env, banco, escolha, dados, API e teste."""
    titulo("Instalacao completa")
    explicar(
        "Vou executar na ordem: pre-requisitos, .env, escolha do banco, subir banco,",
        "criar tabela + dados, subir API e testar. Se um passo falhar, paro ali e",
        "explico o motivo, em vez de seguir acumulando erro.",
    )
    if not verificar_pre_requisitos():
        return
    if not criar_env():
        return
    banco = escolher_banco()
    if not subir_banco(banco):
        return
    if not carregar_dados(banco):
        return
    if banco == "postgres":
        if not subir_api():
            return
        testar_endpoints()
    resumo()


# ---------------------------------------------------------------------------
# 9. Resumo e desinstalacao
# ---------------------------------------------------------------------------

def resumo() -> None:
    """Mostra o estado final: containers, dados e enderecos."""
    titulo("Resumo do que esta no ar")
    banco = banco_atual()
    rodar(comando_compose(banco) + ["ps"], "listar os containers do projeto")

    config = ler_env()
    if banco == "postgres":
        comando = comando_compose(banco) + [
            "exec", "-T", "postgres", "psql",
            "-U", config.get("POSTGRES_USER", "termometro"),
            "-d", config.get("POSTGRES_DB", "termometro"),
            "-c", "SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE tipo='real') AS reais FROM ipca;",
        ]
        rodar(comando, "contar as linhas carregadas na tabela ipca")

    explicar(
        "",
        "Enderecos uteis:",
        "  API:        " + URL_API,
        "  Documentacao: " + URL_API + "/docs",
        "  Rodar o menu de operacao: python meu-loop-agente/workspace/config.py",
        "  Ver o estado do loop:     python meu-loop-agente/verificar_iteracao.py estado",
    )


def desinstalar() -> None:
    """Derruba os containers e, se o usuario confirmar, apaga os dados."""
    titulo("Desinstalacao")
    banco = banco_atual()
    explicar(
        "Vou fazer em duas etapas, e a segunda apaga dados:",
        "  1) parar e remover os containers  -> o banco e a API param de rodar;",
        "  2) remover os VOLUMES             -> apaga os dados gravados no banco.",
        "",
        "O que NAO e apagado: o codigo, o .env, o seed.sql e o arquivo baixado do",
        "Banco Central. Tudo isso continua no disco e pode ser usado de novo.",
    )
    if not confirmar("Deseja mesmo desinstalar (parar os containers)?", padrao_sim=False):
        aviso("nada foi feito.")
        return

    certo, _ = rodar(["docker", "compose", "down"], "parar e remover os containers do PostgreSQL/API")
    if ARQ_COMPOSE_MYSQL.exists():
        rodar(comando_compose("mysql") + ["down"], "parar e remover o container do MySQL")

    if not certo:
        return

    explicar(
        "",
        "Os containers foram removidos, mas os dados continuam no volume.",
        "Se voce subir de novo, o banco volta exatamente como estava.",
    )
    if confirmar("Apagar TAMBEM os dados (remove os volumes)?", padrao_sim=False):
        rodar(["docker", "compose", "down", "-v"], "remover os volumes (apaga os dados do banco)")
        if ARQ_COMPOSE_MYSQL.exists():
            rodar(comando_compose("mysql") + ["down", "-v"], "remover o volume do MySQL")
        ok("dados apagados. Para recomecar: python instalar.py e escolha a opcao 8.")
    else:
        aviso("dados preservados no volume.")


# ---------------------------------------------------------------------------
# Menu principal
# ---------------------------------------------------------------------------

OPCOES = [
    ("1", "Verificar os pre-requisitos (Docker, Python, Compose)"),
    ("2", "Criar/atualizar o arquivo .env"),
    ("3", "Escolher o banco (PostgreSQL ou MySQL)"),
    ("4", "Subir o banco"),
    ("5", "Criar a tabela e carregar os dados (init + seed)"),
    ("6", "Subir a API"),
    ("7", "Testar os 3 endpoints"),
    ("8", "Instalar tudo na ordem (2 a 7)"),
    ("9", "Desinstalar (parar containers e, se quiser, apagar dados)"),
    ("0", "Sair"),
]


def mostrar_menu() -> None:
    """Imprime o menu com uma linha de explicacao em cada opcao."""
    titulo("Instalador do Termometro (Degrau 1)")
    explicar(
        "Escolha o numero da acao. Cada acao explica o que faz antes de agir.",
        "Banco configurado agora: " + banco_atual(),
    )
    print("")
    for numero, descricao in OPCOES:
        print("  " + numero + ") " + descricao)


def main() -> int:
    """Loop do menu. Devolve 0 ao sair normalmente."""
    while True:
        mostrar_menu()
        escolha = perguntar("Opcao", "0")

        if escolha == "0":
            print("")
            print("  Ate logo. Para voltar: python instalar.py")
            return 0
        elif escolha == "1":
            verificar_pre_requisitos()
        elif escolha == "2":
            criar_env()
        elif escolha == "3":
            escolher_banco()
        elif escolha == "4":
            subir_banco()
        elif escolha == "5":
            carregar_dados()
        elif escolha == "6":
            subir_api()
        elif escolha == "7":
            testar_endpoints()
        elif escolha == "8":
            instalar_tudo()
        elif escolha == "9":
            desinstalar()
        else:
            aviso("opcao invalida; escolha um numero do menu.")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("")
        print("  interrompido pelo usuario. Nada foi desfeito.")
        sys.exit(130)
