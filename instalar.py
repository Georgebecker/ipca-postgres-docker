#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""instalar.py — assistente de instalacao do projeto Termometro.

(1) O que e: um programa de terminal que conduz a instalacao passo a passo,
    num menu. Voce escolhe o numero e ele executa.
(2) Para que serve: evita decorar comandos de Docker, SQL e Python, e evita
    esquecer uma etapa (subir o banco sem carregar os dados, por exemplo).
(3) Comparacao: e o assistente de embarque do aeroporto. Voce ainda faz a
    viagem, mas alguem confere o bilhete e diz a ordem certa dos passos.

Como este arquivo conversa com voce (as tres coisas que todo passo tem):
- CONDICIONANTE: antes de agir, ele confere se pode agir (Docker instalado?
  .env existe? banco no ar?). Se nao puder, diz o motivo e para ali.
- MOTIVO: antes de executar, ele diz por que aquele passo existe.
- PADRAO: toda pergunta tem uma resposta padrao (aparece entre colchetes) e
  resposta invalida e explicada, nao ignorada.
- RESULTADO: todo passo termina com [ok], [aviso] ou [erro] — e o [erro] diz o
  que fazer agora, nao apenas que deu errado.

Regras deste arquivo:
- usa SO a biblioteca padrao do Python (nada para instalar antes);
- nada de senha no codigo: ela e pedida na hora e gravada no `.env`;
- nenhum comando destrutivo (apagar dados) roda sem confirmacao explicita.

Uso:
    python instalar.py

Observacao sobre acentos: no console antigo do Windows (pagina de codigo 850)
os acentos podem aparecer como "?". O arquivo esta correto em UTF-8; use o
Windows Terminal ou o terminal do VS Code para ver tudo.
"""

import getpass
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos usados pelo instalador.
# RAIZ e a pasta onde este arquivo esta (a raiz do projeto). Tudo o mais e
# derivado dela, entao o instalador funciona mesmo se o projeto for movido.
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent
ARQ_ENV = RAIZ / ".env"
ARQ_ENV_EXEMPLO = RAIZ / ".env.example"
ARQ_SEED = RAIZ / "meu-loop-agente" / "workspace" / "db" / "seed.sql"
ARQ_RAW = RAIZ / "data" / "raw" / "ipca_433.json"
SCRIPT_BAIXAR = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "baixar_dados.py"
SCRIPT_GERAR_SEED = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "gerar_seed.py"
ARQ_COMPOSE = RAIZ / "docker-compose.yml"
ARQ_COMPOSE_MYSQL = RAIZ / "docker-compose.mysql.yml"
SCRIPT_APLICAR_NUVEM = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "aplicar_sql_nuvem.py"
DIR_API = RAIZ / "meu-loop-agente" / "workspace" / "api"
# O numero do processo (PID) da API local fica na raiz, em um arquivo proprio.
# Detalhe aprendido na pratica: NAO usar ".neon/api.pid" — o CLI do Neon cria
# ".neon" como ARQUIVO de configuracao, e tentar criar um arquivo "dentro" dele
# falha com FileExistsError.
ARQ_PID_API = RAIZ / ".api.pid"

URL_API = "http://localhost:8000"
PORTA_API_PADRAO = 8000
CONTAINER_POSTGRES = "termometro-postgres"
CONTAINER_MYSQL = "termometro-mysql"

# Tempo maximo esperando o banco ficar "healthy" (pronto para receber conexao).
LIMITE_ESPERA_SEGUNDOS = 60
# Tempo maximo esperando a API local comecar a responder.
LIMITE_ESPERA_API_SEGUNDOS = 30

# Chaves que precisam existir no .env para o PostgreSQL funcionar.
CHAVES_POSTGRES = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
# Chaves que precisam existir no .env para o MySQL funcionar.
CHAVES_MYSQL = ("MYSQL_ROOT_PASSWORD", "MYSQL_DATABASE")

# Os dois ambientes que o projeto aceita. A escolha fica no .env, na chave
# AMBIENTE, para que o comportamento nao dependa de adivinhacao.
AMBIENTES = {"docker": "PostgreSQL em Docker (local)", "neon": "PostgreSQL na nuvem (Neon)"}


# ===========================================================================
# 1. Mensagens na tela
#    Cada tipo tem um prefixo fixo, para voce reconhecer de longe o que e
#    informacao, o que e atencao e o que e problema.
# ===========================================================================

def titulo(texto: str) -> None:
    """Abre uma secao na tela. Motivo: separar visualmente um passo do outro."""
    print("")
    print("=" * 64)
    print(texto)
    print("=" * 64)


def explicar(*linhas: str) -> None:
    """Mostra o MOTIVO de um passo, antes de executa-lo.

    Existe para o programa ensinar enquanto trabalha: quem esta instalando pela
    primeira vez precisa entender o que aquele comando faz, nao so ver ele rodar.
    """
    for linha in linhas:
        print("  " + linha)


def ok(mensagem: str) -> None:
    """Resultado POSITIVO: o passo terminou como esperado."""
    print("  [ok] " + mensagem)


def aviso(mensagem: str) -> None:
    """Resultado NEUTRO: algo nao e o ideal, mas nao impede continuar."""
    print("  [aviso] " + mensagem)


def erro(mensagem: str) -> None:
    """Resultado NEGATIVO: o passo falhou e o fluxo sera interrompido."""
    print("  [erro] " + mensagem)


def o_que_fazer(*linhas: str) -> None:
    """Depois de um erro, diz o proximo passo concreto.

    Regra do projeto: mensagem de erro e aula. Dizer apenas "falhou" obriga a
    pessoa a adivinhar; dizer "olhe o log com este comando" resolve.
    """
    for linha in linhas:
        print("         -> " + linha)


# ===========================================================================
# 2. Entrada do usuario
#    Toda pergunta tem PADRAO e resposta invalida e explicada.
# ===========================================================================

def perguntar(pergunta: str, padrao: str = "") -> str:
    """Le uma resposta do teclado. Enter vazio devolve o padrao.

    Motivo do padrao: quem so quer seguir em frente aperta Enter. O valor
    aparece entre colchetes para nao haver duvida sobre o que vai acontecer.
    """
    sufixo = " [" + padrao + "]" if padrao else ""
    resposta = input("  " + pergunta + sufixo + ": ").strip()
    return resposta or padrao


def perguntar_opcao(pergunta: str, validas: tuple, padrao: str = "0") -> str:
    """Pergunta uma opcao e REPETE enquanto a resposta nao for valida.

    Diferente de ignorar o erro em silencio: aqui ele explica qual conjunto e
    aceito. Sem isso, digitar "9" num menu que so aceita 1..8 pareceria que o
    programa "nao fez nada".
    """
    while True:
        resposta = perguntar(pergunta, padrao).strip()
        if resposta in validas:
            return resposta
        erro("opcao invalida: '" + resposta + "'.")
        o_que_fazer("opcoes aceitas: " + ", ".join(validas) + ".",
                    "aperte Enter para usar o padrao (" + padrao + ").")


def confirmar(pergunta: str, padrao_sim: bool = False) -> bool:
    """Pergunta sim/nao, com padrao explicito. Qualquer coisa fora de s/n repete."""
    padrao = "s" if padrao_sim else "n"
    while True:
        resposta = perguntar(pergunta + " (s/n)", padrao).lower()
        if resposta in ("s", "sim", "y", "yes"):
            return True
        if resposta in ("n", "nao", "não", "no"):
            return False
        erro("responda 's' para sim ou 'n' para nao.")
        o_que_fazer("o padrao e '" + padrao + "'; aperte Enter para aceitar.")


# ===========================================================================
# 3. Condicionantes — "posso agir agora?"
#    Cada uma devolve True/False e, quando False, explica o MOTIVO. As acoes
#    chamam estas funcoes antes de rodar qualquer comando de Docker.
# ===========================================================================

def docker_existe() -> bool:
    """Diz se o comando 'docker' esta no PATH desta maquina."""
    return shutil.which("docker") is not None


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


def exigir_docker(motivo: str) -> bool:
    """Condicionante: o Docker esta disponivel?

    Motivo recebido como parametro para a mensagem ficar especifica: "para
    subir o banco" e diferente de "para ler os logs".
    """
    if docker_existe():
        return True
    erro("nao posso continuar: o Docker nao foi encontrado.")
    explicar("  Motivo: " + motivo + ".")
    instrucoes_de_instalacao_do_docker()
    o_que_fazer("instale o Docker, reinicie o terminal e rode o instalador de novo.")
    return False


def exigir_arquivo(caminho: Path, motivo: str) -> bool:
    """Condicionante: o arquivo necessario existe?"""
    if caminho.exists():
        return True
    erro("nao encontrei o arquivo " + str(caminho.name) + ".")
    explicar("  Motivo: " + motivo + ".")
    o_que_fazer("o projeto parece incompleto; recupere o arquivo com:",
                "git checkout -- " + str(caminho.relative_to(RAIZ)))
    return False


def exigir_env(motivo: str) -> bool:
    """Condicionante: o .env existe e tem as chaves do banco escolhido?

    Existe porque o container precisa de usuario, senha e nome do banco. Sem
    elas, o Docker sobe o servico com variavel vazia e a conexao falha depois,
    longe da causa real.
    """
    if not ARQ_ENV.exists():
        erro("nao existe o arquivo .env.")
        explicar("  Motivo: " + motivo + ".",
                 "  O .env guarda usuario, senha e nome do banco.")
        o_que_fazer("rode a opcao 2 do menu para criar o .env.")
        return False

    config = ler_env()
    necessarias = CHAVES_MYSQL if config.get("BANCO", "postgres").lower() == "mysql" else CHAVES_POSTGRES
    faltando = [chave for chave in necessarias if not config.get(chave)]
    if faltando:
        erro("o .env existe, mas falta(m) a(s) chave(s): " + ", ".join(faltando) + ".")
        explicar("  Motivo: " + motivo + ".",
                 "  Sem essas chaves o container sobe com valor vazio.")
        o_que_fazer("rode a opcao 2 do menu para recriar o .env.")
        return False

    return True


def exigir_database_url(motivo: str) -> bool:
    """Condicionante do modo nuvem: existe DATABASE_URL no .env?

    No Neon não existe host, porta e usuário separados para conferir: existe uma
    linha só, com tudo dentro. Sem ela, não há como o script aplicar SQL nem a
    API conectar.
    """
    url = ler_env().get("DATABASE_URL", "").strip()
    if url:
        return True
    erro("nao encontrei DATABASE_URL no .env.")
    explicar("  Motivo: " + motivo + ".",
             "  E nela que ficam host, porta, usuario, senha e nome do banco do Neon.")
    o_que_fazer("rode: neon init   (ele cria o projeto e grava a variavel)",
                "ou copie a connection string no console do Neon e cole no .env.")
    return False


def neon_cli_disponivel() -> bool:
    """Diz se o CLI do Neon esta instalado (usado para login e para conferir)."""
    return shutil.which("neon") is not None


def montar_url_segura(url: str) -> str:
    """Prepara a URL de conexão para o psycopg2: tira prefixo de ORM e garante SSL.

    Dois ajustes que evitam erro na hora de conectar:

    1. `postgresql+psycopg2://` **é sintaxe do SQLAlchemy**, não do psycopg2 puro.
       Este projeto usa psycopg2 direto; se a URL vier com esse sufixo (copiada de
       um projeto que usa ORM), o driver recusa com "invalid URI scheme". Aqui o
       sufixo é removido e a URL volta ao formato que o psycopg2 entende.
    2. O Neon exige conexão criptografada; sem `sslmode` a conexão é recusada com
       uma mensagem que não explica o motivo.
    """
    for prefixo in ("postgresql+psycopg2://", "postgres+psycopg2://"):
        if url.startswith(prefixo):
            url = "postgresql://" + url.split("://", 1)[1]
            break

    if "sslmode=" in url:
        return url
    return url + ("&" if "?" in url else "?") + "sslmode=require"


def comando_neon(*argumentos: str) -> list:
    """Monta o comando do CLI do Neon de um jeito que funcione no Windows.

    Por que isso existe: no Windows, o executavel instalado pelo npm e um arquivo
    .CMD, e o subprocess nao consegue executa-lo diretamente (so .exe). Passando
    pelo cmd.exe, funciona. No Linux/macOS, o comando vai direto.
    """
    if platform.system() == "Windows":
        return ["cmd", "/c", "neon"] + list(argumentos)
    return ["neon"] + list(argumentos)


def biblioteca_psycopg2_disponivel() -> bool:
    """Diz se a psycopg2 esta instalada (o script prefere ela para falar com o banco)."""
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        return False
    return True


# ===========================================================================
# 4. Execucao de comandos
# ===========================================================================

def rodar(comando: list, motivo: str, entrada: bytes = None,
          dica_se_falhar: str = "") -> tuple:
    """Executa um comando na raiz do projeto e devolve (deu_certo, saida).

    Motivo: impresso antes, para o usuario saber POR QUE aquele comando roda.
    Dica: impressa depois, so quando falha, dizendo o que fazer agora.
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
        erro("o programa '" + comando[0] + "' nao foi encontrado no PATH.")
        o_que_fazer(dica_se_falhar or "confira se o programa esta instalado.")
        return False, ""
    except subprocess.TimeoutExpired:
        erro("o comando passou de 10 minutos e foi interrompido.")
        o_que_fazer("verifique se o Docker Desktop travou e tente de novo.")
        return False, ""

    saida = (resultado.stdout or b"").decode("utf-8", "replace")
    erros = (resultado.stderr or b"").decode("utf-8", "replace")
    texto = (saida + "\n" + erros).strip()

    if resultado.returncode != 0:
        erro("o comando terminou com codigo " + str(resultado.returncode) + ".")
        print("         ultimas linhas da saida:")
        for linha in texto.splitlines()[-6:]:
            print("           " + linha)
        o_que_fazer(dica_se_falhar or "leia a saida acima e corrija o que ela aponta.")
        return False, texto

    ok("comando concluido com sucesso.")
    return True, texto


# ===========================================================================
# 5. Leitura e escrita do .env
# ===========================================================================

def ler_env() -> dict:
    """Le o `.env` e devolve um dicionario chave -> valor.

    Linhas comecando com '#' e linhas vazias sao ignoradas. Se o arquivo nao
    existe, devolve dicionario vazio (quem chama decide o que fazer).

    Aspas envolventes sao removidas: o `neon init` grava
    DATABASE_URL="postgresql://..." e as aspas NAO fazem parte do valor.
    """
    dados = {}
    if not ARQ_ENV.exists():
        return dados
    for linha in ARQ_ENV.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        valor = valor.strip()
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in ('"', "'"):
            valor = valor[1:-1]
        dados[chave.strip()] = valor
    return dados


def definir_no_env(chave: str, valor: str) -> None:
    """Grava (ou substitui) uma chave no `.env`, preservando o resto do arquivo.

    Substituir no lugar e melhor que reescrever tudo: os comentarios que o dono
    escreveu continuam onde estavam.
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


def banco_atual() -> str:
    """Le do `.env` qual banco foi escolhido; padrao postgres."""
    return ler_env().get("BANCO", "postgres").lower()


def ambiente_atual() -> str:
    """Diz qual ambiente esta configurado: 'docker' (local) ou 'neon' (nuvem).

    Ordem de decisao, do mais explicito para o mais implicito:
    1. a chave AMBIENTE no .env, se existir (escolha consciente do dono);
    2. a presenca de DATABASE_URL, que e o que o Neon entrega;
    3. 'docker', como padrao historico do projeto.

    Por que nao decidir so pela DATABASE_URL: o .env pode ter as duas coisas
    (banco local e nuvem), e a presenca de uma URL nao diz qual voce quer usar
    agora. A chave AMBIENTE diz.
    """
    dados = ler_env()
    escolhido = (dados.get("AMBIENTE") or "").strip().lower()
    if escolhido in AMBIENTES:
        return escolhido
    if dados.get("DATABASE_URL"):
        return "neon"
    return "docker"


def escolher_ambiente() -> str:
    """Pergunta onde o banco vai viver e grava a escolha no `.env`. Devolve o nome.

    Por que perguntar em vez de adivinhar: o .env pode ter as duas configuracoes
    (a local e a da nuvem). Sem uma escolha explicita, o instalador faria algo
    diferente do que voce espera — e a culpa pareceria do programa.
    """
    titulo("Escolha do ambiente")
    explicar(
        "Motivo: o projeto funciona nos dois lugares, e o passo a passo muda:",
        "",
        "1) Docker local — PostgreSQL dentro de um container na sua maquina:",
        "   - treina container, volume e healthcheck (o objetivo original do degrau);",
        "   - exige o Docker Desktop instalado e funcionando.",
        "",
        "2) Neon (nuvem) — PostgreSQL gerenciado, plano gratuito:",
        "   - nenhuma instalacao de banco; funciona por uma URL de conexao;",
        "   - exige internet e a variavel DATABASE_URL no .env;",
        "   - nao exercita Docker.",
        "",
        "Ambiente configurado agora: " + ambiente_atual() + ".",
    )

    escolha = perguntar_opcao("Qual ambiente? 1 = Docker local, 2 = Neon", ("1", "2"),
                              "1" if ambiente_atual() == "docker" else "2")
    ambiente = "docker" if escolha == "1" else "neon"
    definir_no_env("AMBIENTE", ambiente)
    ok("ambiente escolhido: " + ambiente + " (gravado no .env como AMBIENTE)")

    if ambiente == "neon":
        aviso("o modo nuvem nao usa Docker.")
        o_que_fazer("garanta DATABASE_URL no .env (o comando 'neon init' grava).",
                    "a API vai rodar na sua maquina, em Python, falando com o banco na nuvem.")
        return ambiente

    # No modo Docker ainda existe a escolha do banco (PostgreSQL ou MySQL).
    explicar(
        "",
        "Agora o banco do container:",
        "  1) PostgreSQL — padrao do projeto, com tudo pronto;",
        "  2) MySQL — extra opcional para comparar os dois dialetos de SQL.",
    )
    escolha_banco = perguntar_opcao("Qual banco? 1 = PostgreSQL, 2 = MySQL", ("1", "2"), "1")
    banco = "mysql" if escolha_banco == "2" else "postgres"
    definir_no_env("BANCO", banco)
    ok("banco do container: " + banco)
    return ambiente


def comando_compose(banco: str) -> list:
    """Monta o comando do Docker Compose certo para o banco escolhido."""
    if banco == "mysql":
        return ["docker", "compose", "-f", "docker-compose.mysql.yml"]
    return ["docker", "compose"]


# ===========================================================================
# 6. Opcao 1 — verificar pre-requisitos
# ===========================================================================

def verificar_pre_requisitos(ambiente: str = None) -> bool:
    """Confere o que o ambiente escolhido exige. Devolve True se tudo existe.

    Cada ambiente tem exigencias diferentes, e o instalador diz qual esta
    conferindo:
    - Docker local: Docker instalado, Compose respondendo e as pecas do .env;
    - Neon: DATABASE_URL no .env e uma forma de falar com o banco (psycopg2 ou
      o CLI do Neon).
    """
    ambiente = ambiente or ambiente_atual()
    titulo("Verificacao dos pre-requisitos — " + AMBIENTES[ambiente])
    explicar(
        "Motivo: instalar sem conferir a base e a receita para um erro confuso",
        "mais adiante ('nao conecta' sem dizer por que).",
    )

    problemas = 0

    # Condicionante comum aos dois ambientes: versao do Python.
    versao = sys.version_info
    if versao >= (3, 8):
        ok("Python " + platform.python_version() + " (minimo 3.8)")
    else:
        erro("Python " + platform.python_version() + " e antigo.")
        o_que_fazer("instale Python 3.8 ou mais novo em https://python.org")
        problemas += 1

    if ambiente == "neon":
        # Condicionante 1 do Neon: a URL de conexao.
        if exigir_database_url("sem ela a API e os scripts nao sabem onde esta o banco"):
            ok("DATABASE_URL encontrada no .env")

        # Condicionante 2 do Neon: alguma forma de falar com o banco.
        if biblioteca_psycopg2_disponivel():
            ok("biblioteca psycopg2 disponivel (caminho preferido)")
        elif neon_cli_disponivel():
            aviso("psycopg2 nao instalada; vou usar o CLI do Neon como alternativa.")
            o_que_fazer("para instalar: pip install psycopg2-binary")
        else:
            erro("nem psycopg2 nem o CLI do Neon estao disponiveis.")
            o_que_fazer("instale uma das duas opcoes:",
                        "  pip install psycopg2-binary",
                        "  npm i -g neon")
            problemas += 1

        # O CLI e opcional no Neon: se existir, confere se a sessao esta ativa.
        if neon_cli_disponivel():
            certo, _ = rodar(comando_neon("me"),
                             "conferir se o CLI do Neon esta autenticado",
                             dica_se_falhar="rode: neon login")
            if certo:
                ok("CLI do Neon autenticado")
            else:
                aviso("o CLI do Neon nao esta autenticado (nao impede o modo nuvem).")
                o_que_fazer("para usar os comandos do Neon: neon login")
    else:
        # Modo Docker: as condicionantes de sempre.
        if docker_existe():
            ok("Docker encontrado")
        else:
            erro("o comando 'docker' nao foi encontrado.")
            instrucoes_de_instalacao_do_docker()
            problemas += 1
            # Sem Docker nao adianta testar o compose: o erro seria repetido.
            print("")
            erro("verificacao interrompida: " + str(problemas) + " problema(s) encontrado(s).")
            o_que_fazer("resolva o item acima e rode a verificacao de novo.",
                        "se preferir seguir sem Docker, use a opcao 3 (ambiente Neon).")
            return False

        certo, _ = rodar(["docker", "compose", "version"],
                         "conferir se o Docker Compose responde",
                         dica_se_falhar="abra o Docker Desktop e espere o icone ficar verde.")
        if certo:
            ok("Docker Compose responde")
        else:
            erro("o 'docker compose' nao respondeu.")
            explicar("  Motivo: o Docker Desktop pode estar iniciando, ou a versao e antiga.")
            o_que_fazer("espere o Docker Desktop ficar verde e rode de novo.",
                        "se persistir, atualize o Docker.")
            problemas += 1

        if not exigir_env("o container precisa de usuario, senha e nome do banco"):
            problemas += 1

    print("")
    if problemas == 0:
        ok("tudo certo para o ambiente " + ambiente + ".")
        return True
    erro(str(problemas) + " problema(s) encontrado(s).")
    o_que_fazer("resolva os itens marcados com [erro] e rode de novo.")
    return False


# ===========================================================================
# 7. Opcao 2 — criar o .env
# ===========================================================================

def criar_env() -> bool:
    """Cria o `.env` a partir do `.env.example` e pergunta a senha do banco."""
    titulo("Configuracao do arquivo .env")
    explicar(
        "Motivo: o Docker precisa saber usuario, senha e nome do banco.",
        "O '.env' fica so na sua maquina e nunca vai para o GitHub.",
        "",
        "Vou copiar o modelo '.env.example' e trocar a senha pela sua.",
    )

    # Condicionante: o modelo precisa existir.
    if not exigir_arquivo(ARQ_ENV_EXEMPLO, "e ele que lista todas as chaves necessarias"):
        return False

    # Condicionante: se o .env ja existe, perguntar antes de sobrescrever.
    if ARQ_ENV.exists():
        aviso("o .env ja existe.")
        explicar("  Sobrescrever apaga o que voce configurou, inclusive a senha atual.")
        if not confirmar("Recriar o .env do zero?", padrao_sim=False):
            ok("mantive o .env atual (nada foi alterado).")
            return True

    shutil.copyfile(str(ARQ_ENV_EXEMPLO), str(ARQ_ENV))
    ok(".env criado a partir do .env.example")

    # Aviso ANTES de pedir a senha: o getpass nao ecoa o que foi digitado.
    # Sem este aviso, a tela parece travada e a pessoa acha que o programa morreu.
    print("")
    aviso("ATENCAO: a proxima linha pede a senha e NAO mostra o que voce digita.")
    explicar(
        "  Digite a senha e aperte Enter. Nada aparece enquanto digita — isso e",
        "  normal e proposital (ninguem ao lado consegue ler).",
        "  Se preferir manter a senha de exemplo do arquivo, apenas aperte Enter.",
    )
    print("")

    if not sys.stdin.isatty():
        aviso("este terminal nao permite entrada escondida (stdin nao e interativo).")
        o_que_fazer("rode o instalador em um terminal de verdade,",
                    "ou edite POSTGRES_PASSWORD direto no .env.")
        senha = ""
    else:
        senha = getpass.getpass("  Senha do banco: ").strip()
    if not senha:
        aviso("senha vazia: mantive o marcador 'troque_esta_senha'.")
        o_que_fazer("troque esse valor no .env antes de subir o banco em producao.")
    else:
        definir_no_env("POSTGRES_PASSWORD", senha)
        definir_no_env("MYSQL_ROOT_PASSWORD", senha)
        ok("senha gravada no .env (PostgreSQL e MySQL)")

    explicar(
        "",
        "Lembrete: o .env nunca deve ser commitado. Se ele aparecer no",
        "'git status' como arquivo novo, algo esta errado.",
    )
    return True


# ===========================================================================
# 8. Opcao 3 — escolher o banco
# ===========================================================================

# ===========================================================================
# 9. Opcao 4 — subir o banco
# ===========================================================================

def esperar_banco(banco: str) -> bool:
    """Espera o banco responder ao healthcheck, ate o limite de tempo.

    Healthcheck e a verificacao automatica que o Docker faz de tempos em tempos.
    Enquanto ele nao diz 'healthy', qualquer conexao seria recusada.
    """
    container = CONTAINER_MYSQL if banco == "mysql" else CONTAINER_POSTGRES
    print("")
    print("  # esperando o banco ficar pronto (healthcheck)")
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
    explicar("  Motivo: o container subiu, mas o servico de banco nao terminou de iniciar.")
    o_que_fazer("veja o que aconteceu com:",
                "docker compose logs " + ("mysql" if banco == "mysql" else "postgres"))
    return False


def subir_banco(banco: str = None) -> bool:
    """Sobe o container do banco escolhido."""
    banco = banco or banco_atual()
    titulo("Subindo o banco (" + banco + ")")
    explicar(
        "Motivo: sem o banco no ar, nao ha onde criar a tabela nem carregar os dados.",
        "Na primeira vez o Docker baixa a imagem (pode demorar alguns minutos).",
    )

    # Condicionantes: arquivo do compose, .env e Docker.
    arquivo = ARQ_COMPOSE_MYSQL if banco == "mysql" else ARQ_COMPOSE
    if not exigir_arquivo(arquivo, "e ele que descreve o container do banco"):
        return False
    if not exigir_env("o container precisa de usuario, senha e nome do banco"):
        return False
    if not exigir_docker("o banco roda dentro de um container"):
        return False

    certo, _ = rodar(
        comando_compose(banco) + ["up", "-d", banco],
        "subir o container do banco em segundo plano (-d)",
        dica_se_falhar="veja o log com: docker compose logs " + banco,
    )
    if not certo:
        erro("o banco NAO subiu.")
        return False

    if not esperar_banco(banco):
        return False

    ok("banco no ar e pronto para receber conexao.")
    return True


def preparar_banco_neon() -> bool:
    """No modo nuvem nao ha container para subir: confere a conexao e pronto.

    Motivo de existir mesmo assim: o menu precisa de um passo previsivel no
    mesmo lugar. Aqui ele faz o equivalente ao "subir o banco" — so que, em vez
    de iniciar algo, prova que o banco da nuvem responde.
    """
    titulo("Preparando o banco na nuvem (Neon)")
    explicar(
        "Motivo: no Neon nao existe container local para iniciar. O banco ja esta",
        "no ar do outro lado; o que precisa ser provado e que a URL do .env conecta.",
        "",
        "Vou abrir uma conexao e perguntar a versao do PostgreSQL. Se responder,",
        "o caminho ate o banco esta livre.",
    )

    if not exigir_database_url("e ela que aponta para o banco na nuvem"):
        return False

    url = montar_url_segura(ler_env().get("DATABASE_URL", "").strip())

    if biblioteca_psycopg2_disponivel():
        import psycopg2

        print("")
        print("  # conectar ao banco da nuvem e perguntar a versao")
        try:
            with psycopg2.connect(url) as conexao:
                with conexao.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    versao = cursor.fetchone()[0]
        except psycopg2.Error as falha:
            erro("nao consegui conectar no banco da nuvem.")
            print("         " + str(falha).strip().splitlines()[0])
            o_que_fazer("confira a DATABASE_URL no .env (senha e host precisam estar certos).",
                        "se o projeto foi apagado no console do Neon, crie outro com 'neon init'.")
            return False
        ok("conectado: " + versao.split(" on ")[0])
        return True

    # Alternativa sem psycopg2: usa o CLI do Neon, que ja guardou as credenciais.
    if not neon_cli_disponivel():
        erro("sem psycopg2 e sem o CLI do Neon, nao ha como falar com o banco.")
        o_que_fazer("pip install psycopg2-binary   ou   npm i -g neon")
        return False

    certo, _ = rodar(
        comando_neon("projects", "list"),
        "conferir se o CLI do Neon responde (conexao com a nuvem)",
        dica_se_falhar="rode: neon login",
    )
    if not certo:
        erro("o CLI do Neon nao respondeu.")
        return False
    ok("CLI do Neon respondeu; o banco da nuvem esta acessivel.")
    return True


def preparar_banco(ambiente: str = None) -> bool:
    """Despacha o passo 4 para o ambiente escolhido."""
    ambiente = ambiente or ambiente_atual()
    if ambiente == "neon":
        return preparar_banco_neon()
    return subir_banco()


# ===========================================================================
# 10. Opcao 5 — estrutura + seed
# ===========================================================================

def aplicar_sql(banco: str, arquivo: Path, motivo: str) -> bool:
    """Envia um arquivo .sql para dentro do container do banco.

    O arquivo e lido aqui e passado pela entrada padrao, em vez de depender de
    redirecionamento do shell. Assim funciona igual no PowerShell, no cmd e no
    bash.
    """
    if not exigir_arquivo(arquivo, "sem ele nao ha o que aplicar no banco"):
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

    certo, saida = rodar(
        comando,
        motivo,
        entrada=conteudo,
        dica_se_falhar="o container do banco esta rodando? use a opcao 4 antes.",
    )
    if not certo:
        erro("o arquivo " + arquivo.name + " NAO foi aplicado.")
        return False

    ok(arquivo.name + " aplicado sem erro.")
    return True


def carregar_dados(ambiente: str = None, banco: str = None) -> bool:
    """Aplica a estrutura (init) e depois o seed — no ambiente escolhido.

    Docker: envia o SQL por `psql` dentro do container.
    Neon:   chama o script `aplicar_sql_nuvem.py`, que usa a DATABASE_URL.
    """
    ambiente = ambiente or ambiente_atual()
    if ambiente == "neon":
        titulo("Criando a tabela e carregando os dados (nuvem)")
        explicar(
            "Motivo: mesma necessidade do modo Docker — sem tabela e sem dados, a",
            "API nao tem o que responder.",
            "",
            "Como funciona: o script aplicar_sql_nuvem.py le o init.sql e o seed.sql e",
            "envia pela DATABASE_URL. Nao ha container nem psql para usar.",
        )
        if not exigir_database_url("o script precisa saber em qual banco escrever"):
            return False
        certo, _ = rodar(
            [sys.executable, str(SCRIPT_APLICAR_NUVEM)],
            "aplicar init.sql e seed.sql no banco da nuvem",
            dica_se_falhar="veja o erro do script acima; ele indica qual passo falhou.",
        )
        if not certo:
            erro("a carga no banco da nuvem NAO terminou.")
            return False
        ok("estrutura e dados aplicados no banco da nuvem.")
        return True

    banco = banco or banco_atual()
    titulo("Criando a tabela e carregando os dados")
    explicar(
        "Motivo: o banco sobe vazio. Sem estes dois passos ele nao tem tabela",
        "nem conteudo para a API consultar.",
        "",
        "Duas etapas:",
        "  1) init.sql -> cria a tabela ipca (PK, UNIQUE em data, NUMERIC, CHECK, indice);",
        "  2) seed.sql -> insere os 561 meses reais + 2 ficticios de 2099.",
        "",
        "Reaplicar os dois e seguro: a criacao usa IF NOT EXISTS e a insercao",
        "ignora mes que ja existe. Nada duplica.",
    )

    if not exigir_docker("aplicar SQL exige o banco rodando em container"):
        return False
    if not exigir_env("o comando psql/mysql precisa do usuario e do nome do banco"):
        return False

    pasta = "mysql" if banco == "mysql" else ""
    inicial = RAIZ / "meu-loop-agente" / "workspace" / "db" / pasta / "init.sql"
    if not aplicar_sql(banco, inicial, "criar a tabela ipca (idempotente)"):
        return False

    # Condicionante: o seed precisa existir e estar no dialeto certo.
    if not ARQ_SEED.exists():
        aviso("seed.sql nao existe; vou gerar agora a partir do raw.")
        if not ARQ_RAW.exists():
            explicar("  O dado bruto ainda nao foi baixado. Baixando agora...")
            if not rodar([sys.executable, str(SCRIPT_BAIXAR)],
                         "baixar a serie 433 do Banco Central")[0]:
                return False
        if not rodar([sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", banco],
                     "gerar o seed.sql no dialeto " + banco)[0]:
            return False
    else:
        cabecalho = ARQ_SEED.read_text(encoding="utf-8", errors="replace")[:300]
        if ("Dialeto: " + banco) not in cabecalho:
            aviso("o seed.sql esta em outro dialeto; regenerando para " + banco + ".")
            if not rodar([sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", banco],
                         "regenerar o seed.sql no dialeto certo")[0]:
                return False

    if not aplicar_sql(banco, ARQ_SEED, "inserir os dados (ignora o que ja existe)"):
        return False

    ok("tabela criada e dados carregados.")
    return True


# ===========================================================================
# 11. Opcao 6 — subir a API
# ===========================================================================

def api_esta_no_ar() -> bool:
    """Diz se a API ja responde em /health (usado antes de subir de novo)."""
    try:
        with urllib.request.urlopen(URL_API + "/health", timeout=3) as resposta:
            return resposta.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def iniciar_api_local() -> bool:
    """Sobe a API com Uvicorn na sua maquina, apontando para o banco da nuvem.

    Por que Uvicorn direto e nao container: no modo Neon nao ha Docker. A API e
    um programa Python comum; o Uvicorn e o servidor que a deixa acessivel.

    O processo fica em segundo plano e o numero dele (PID) e gravado em
    `.neon/api.pid`, para a opcao 9 conseguir parar depois. Sem esse arquivo,
    sobraria um servidor rodando sem ninguem saber como encerrar.
    """
    titulo("Subindo a API localmente (sem Docker)")
    explicar(
        "Motivo: a API continua rodando na sua maquina; so o BANCO esta na nuvem.",
        "O Uvicorn e o servidor que publica a API em " + URL_API + ".",
    )

    if not exigir_database_url("a API le o banco pela DATABASE_URL"):
        return False

    if api_esta_no_ar():
        ok("a API ja esta respondendo em " + URL_API + " — nao vou subir outra.")
        return True

    if not exigir_arquivo(DIR_API / "app" / "main.py", "e o ponto de entrada da aplicacao"):
        return False

    comando = [sys.executable, "-m", "uvicorn", "app.main:app",
               "--host", "127.0.0.1", "--port", str(PORTA_API_PADRAO)]
    print("")
    print("  # iniciar a API em segundo plano")
    print("  $ " + " ".join(comando))
    try:
        processo = subprocess.Popen(
            comando,
            cwd=str(DIR_API),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except OSError as falha:
        erro("nao consegui iniciar o Uvicorn: " + str(falha))
        o_que_fazer("confira se fastapi e uvicorn estao instalados:",
                    "  pip install -r meu-loop-agente/workspace/api/requirements.txt")
        return False

    ARQ_PID_API.write_text(str(processo.pid), encoding="utf-8")

    print("  # esperando a API responder (ate " + str(LIMITE_ESPERA_API_SEGUNDOS) + "s)")
    limite = time.time() + LIMITE_ESPERA_API_SEGUNDOS
    while time.time() < limite:
        if api_esta_no_ar():
            ok("API no ar em " + URL_API + " (PID " + str(processo.pid) + ")")
            o_que_fazer("para parar depois: opcao 9 deste menu.",
                        "documentacao interativa: " + URL_API + "/docs")
            return True
        if processo.poll() is not None:
            # O processo morreu: provavelmente faltou biblioteca ou o import falhou.
            saida = b""
            if processo.stdout is not None:
                saida = processo.stdout.read() or b""
            erro("a API encerrou sozinha antes de responder.")
            for linha in saida.decode("utf-8", "replace").splitlines()[-6:]:
                print("         " + linha)
            o_que_fazer("instale as dependencias da API:",
                        "  pip install -r meu-loop-agente/workspace/api/requirements.txt")
            return False
        time.sleep(1)

    erro("a API nao respondeu em " + str(LIMITE_ESPERA_API_SEGUNDOS) + " segundos.")
    o_que_fazer("veja o processo: PID " + str(processo.pid),
                "para encerrar: opcao 9 deste menu.")
    return False


def parar_api_local() -> None:
    """Encerra a API que foi iniciada pela opcao 6 (se ela estiver rodando)."""
    if not ARQ_PID_API.exists():
        aviso("nao ha registro de API iniciada por este instalador.")
        return
    try:
        pid = int(ARQ_PID_API.read_text(encoding="utf-8").strip())
    except ValueError:
        aviso("o arquivo .neon/api.pid esta invalido; vou apaga-lo.")
        ARQ_PID_API.unlink(missing_ok=True)
        return

    if platform.system() == "Windows":
        comando = ["taskkill", "/PID", str(pid), "/F"]
    else:
        comando = ["kill", str(pid)]

    certo, _ = rodar(comando, "encerrar a API local (PID " + str(pid) + ")",
                     dica_se_falhar="o processo pode ja ter sido encerrado manualmente.")
    if certo:
        ok("API local encerrada.")
    ARQ_PID_API.unlink(missing_ok=True)


def subir_api(ambiente: str = None) -> bool:
    """Sobe a API no ambiente escolhido: container (Docker) ou Uvicorn (Neon)."""
    ambiente = ambiente or ambiente_atual()
    if ambiente == "neon":
        return iniciar_api_local()

    titulo("Subindo a API")

    # Condicionante: a API depende do PostgreSQL.
    if banco_atual() == "mysql":
        aviso("a API deste projeto le do PostgreSQL; com BANCO=mysql ela nao sobe.")
        explicar("  Motivo: o extra de MySQL serve para estudar o banco, nao o projeto todo.")
        o_que_fazer("escolha a opcao 3 e selecione PostgreSQL para subir a API.")
        return False

    if not exigir_docker("a API roda dentro de um container"):
        return False
    if not exigir_env("a API le usuario e senha do banco a partir do .env"):
        return False

    explicar(
        "Motivo: a API e um processo separado; o container garante que ela",
        "tenha as bibliotecas certas, sem instalar nada na sua maquina.",
        "A primeira construcao demora; as seguintes reaproveitam o que ja existe.",
    )
    certo, _ = rodar(
        ["docker", "compose", "up", "-d", "--build", "api"],
        "construir a imagem e subir a API",
        dica_se_falhar="veja o erro de build com: docker compose build api",
    )
    if not certo:
        erro("a API NAO subiu.")
        return False

    ok("API no ar em " + URL_API)
    return True


# ===========================================================================
# 12. Opcao 7 — testar os endpoints
# ===========================================================================

def testar_endpoints() -> bool:
    """Faz uma chamada em cada um dos 3 endpoints e mostra o que voltou."""
    titulo("Testando os 3 endpoints")
    explicar(
        "Motivo: e a prova final. Container de pe nao garante que a API responde.",
        "Vou chamar os tres e mostrar o status HTTP (200 = deu certo).",
    )
    caminhos = ["/health", "/ipca/ultimo", "/ipca/serie?tipo=real"]
    aprovados = 0

    for caminho in caminhos:
        url = URL_API + caminho
        print("")
        print("  # chamar " + url)
        try:
            with urllib.request.urlopen(url, timeout=10) as resposta:
                corpo = resposta.read().decode("utf-8", "replace")
                status = resposta.status
        except urllib.error.HTTPError as falha:
            erro(caminho + " -> HTTP " + str(falha.code) + " (o pedido chegou, a resposta foi de erro).")
            continue
        except urllib.error.URLError:
            erro(caminho + " -> sem conexao (a API nao esta no ar?).")
            o_que_fazer("suba a API com a opcao 6 e tente de novo.")
            continue

        if status == 200:
            aprovados += 1
            ok(caminho + " -> 200 | " + corpo[:90] + ("..." if len(corpo) > 90 else ""))
        else:
            aviso(caminho + " -> HTTP " + str(status) + " (200 era o esperado).")

    print("")
    print("  resultados: " + str(aprovados) + " de " + str(len(caminhos)) + " endpoints responderam.")
    if aprovados == len(caminhos):
        ok("tudo respondendo: o degrau esta verificavel de ponta a ponta.")
        return True

    erro("nem todos os endpoints responderam.")
    if ambiente_atual() == "neon":
        o_que_fazer("suba a API com a opcao 6 (Uvicorn local).",
                    "se ela ja estiver rodando, veja a janela/processo do Uvicorn;",
                    "para reiniciar do zero: opcao 9 e depois opcao 6.")
    else:
        o_que_fazer("veja o log da API: docker compose logs --tail=30 api")
    return False


# ===========================================================================
# 13. Opcao 8 — instalacao completa
# ===========================================================================

def instalar_tudo() -> None:
    """Roda a sequencia inteira, anunciando cada etapa e dizendo onde parou.

    Motivo desta funcao ser tao verbosa: instalar e uma fila de passos e, quando
    um falha, a pessoa precisa saber DUAS coisas — em qual passo parou e que
    nada foi desfeito. Sem isso, o retorno ao menu parece "nao fez nada".
    """
    titulo("Instalacao completa")
    explicar(
        "Motivo: fazer tudo na ordem certa, uma vez, sem esquecer etapa.",
        "Sao 6 etapas. Vou anunciar cada uma antes de comecar e, se alguma falhar,",
        "digo exatamente onde parei — em vez de acumular erro sobre erro.",
    )

    concluidas = []

    def interromper(numero: str, descricao: str) -> None:
        """Anuncia a interrupcao, lista o que deu certo e o proximo passo."""
        print("")
        erro("INSTALACAO INTERROMPIDA na etapa " + numero + " (" + descricao + ").")
        if concluidas:
            explicar("  Ja deu certo antes disso:")
            for item in concluidas:
                print("    - " + item)
        else:
            explicar("  Nenhuma etapa foi concluida ainda.")
        explicar("  Nada foi desfeito: containers, arquivos e dados continuam como estavam.")
        o_que_fazer("resolva o problema mostrado acima e rode a opcao 8 de novo.",
                    "a instalacao pode ser repetida: nada duplica.")

    def etapa(numero: str, descricao: str, acao) -> bool:
        """Anuncia a etapa, executa e reporta o resultado. Devolve se deu certo."""
        print("")
        print("  ---------------- etapa " + numero + ": " + descricao + " ----------------")
        try:
            certo = bool(acao())
        except Exception as falha:  # rede de seguranca por etapa
            erro("erro inesperado nesta etapa: " + type(falha).__name__ + " - " + str(falha))
            certo = False
        if certo:
            concluidas.append("etapa " + numero + ": " + descricao)
        return certo

    if not etapa("1/6", "verificar os pre-requisitos", verificar_pre_requisitos):
        interromper("1/6", "pre-requisitos")
        return

    if not etapa("2/6", "criar o arquivo .env", criar_env):
        interromper("2/6", "arquivo .env")
        return

    print("")
    print("  ---------------- etapa 3/6: escolher o ambiente ----------------")
    ambiente = escolher_ambiente()
    concluidas.append("etapa 3/6: ambiente escolhido (" + ambiente + ")")

    if not etapa("4/6", "preparar o banco", lambda: preparar_banco(ambiente)):
        interromper("4/6", "preparar o banco (" + ambiente + ")")
        return

    if not etapa("5/6", "criar a tabela e carregar os dados", lambda: carregar_dados(ambiente)):
        interromper("5/6", "carga dos dados")
        return

    if ambiente == "neon" or banco_atual() == "postgres":
        if not etapa("6/6", "subir a API e testar os endpoints",
                     lambda: subir_api(ambiente) and testar_endpoints()):
            interromper("6/6", "API / endpoints")
            return
    else:
        aviso("banco MySQL instalado; a API nao entra neste modo (ela le do PostgreSQL).")

    print("")
    ok("as 6 etapas terminaram sem erro.")
    resumo()


# ===========================================================================
# 14. Opcao 9 — resumo e desinstalacao
# ===========================================================================

def resumo() -> None:
    """Mostra o estado final: ambiente, containers (ou conexao) e dados."""
    titulo("Resumo do que esta no ar")
    ambiente = ambiente_atual()
    ok("ambiente: " + AMBIENTES[ambiente])

    if ambiente == "neon":
        # No modo nuvem nao ha container: o "estado" e a conexao e a contagem.
        if exigir_database_url("estamos conferindo o banco da nuvem"):
            url = montar_url_segura(ler_env().get("DATABASE_URL", "").strip())
            if biblioteca_psycopg2_disponivel():
                import psycopg2
                try:
                    with psycopg2.connect(url) as conexao:
                        with conexao.cursor() as cursor:
                            cursor.execute("SELECT COUNT(*) FROM ipca;")
                            total = cursor.fetchone()[0]
                    esperado = 563
                    if total == esperado:
                        ok("tabela ipca com " + str(total) + " linhas (esperado: " + str(esperado) + ")")
                    else:
                        aviso("tabela ipca com " + str(total) + " linhas; o esperado era " + str(esperado) + ".")
                        o_que_fazer("rode a opcao 5 para recarregar o seed.")
                except psycopg2.Error as falha:
                    aviso("nao consegui contar as linhas: " + str(falha).strip().splitlines()[0])
        print("")
        print("  # testar os 3 endpoints")
        rodar([sys.executable, str(SCRIPT_MEDIR)], "medir quantos endpoints respondem")
    else:
        banco = banco_atual()
        certo, _ = rodar(comando_compose(banco) + ["ps"], "listar os containers do projeto")
        if not certo:
            aviso("nao consegui listar os containers; veja o erro acima.")
            return

        config = ler_env()
        if banco == "postgres":
            comando = comando_compose(banco) + [
                "exec", "-T", "postgres", "psql",
                "-U", config.get("POSTGRES_USER", "termometro"),
                "-d", config.get("POSTGRES_DB", "termometro"),
                "-t", "-A", "-c",
                "SELECT COUNT(*) FROM ipca;",
            ]
            certo, saida = rodar(comando, "contar as linhas carregadas na tabela ipca")
            if certo and saida.strip().isdigit():
                total = saida.strip().splitlines()[-1]
                esperado = 563
                if int(total) == esperado:
                    ok("tabela ipca com " + total + " linhas (esperado: " + str(esperado) + ")")
                else:
                    aviso("tabela ipca com " + total + " linhas; o esperado era " + str(esperado) + ".")
                    o_que_fazer("rode a opcao 5 para recarregar o seed.")

    explicar(
        "",
        "Enderecos uteis:",
        "  API:          " + URL_API,
        "  Documentacao: " + URL_API + "/docs",
        "  Menu do dia a dia: python meu-loop-agente/workspace/config.py",
        "  Estado do loop:    python meu-loop-agente/verificar_iteracao.py estado",
    )


def desinstalar(ambiente: str = None) -> None:
    """Encerra o que roda NA SUA MÁQUINA. O banco da nuvem não é afetado.

    No modo Neon não existe nada para "derrubar" do lado do banco: ele vive no
    servidor do Neon e continua lá. O que este menu encerra é o processo local
    da API (Uvicorn). Se você quiser apagar os DADOS, isso é uma decisão à parte,
    feita com SQL (DROP TABLE) — e não é papel de um instalador.
    """
    ambiente = ambiente or ambiente_atual()
    if ambiente == "neon":
        titulo("Parar o ambiente local (banco na nuvem)")
        explicar(
            "Motivo: liberar a porta 8000 e encerrar o Uvicorn que esta na sua maquina.",
            "",
            "O banco do Neon NAO e afetado: ele esta no servidor do Neon e continua",
            "existindo, com todos os dados. Para apagar as tabelas algum dia, o",
            "caminho e SQL, nao um menu:",
            "    DROP TABLE ipca;",
        )
        parar_api_local()
        ok("ambiente local encerrado. Banco da nuvem preservado.")
        return

    titulo("Desinstalacao")

    if not exigir_docker("parar containers exige o Docker"):
        return

    banco = banco_atual()
    explicar(
        "Motivo: liberar espaco e encerrar o ambiente quando voce nao precisa mais.",
        "",
        "Vou fazer em duas etapas, e a segunda apaga dados:",
        "  1) remover os containers -> banco e API param de rodar;",
        "  2) remover os VOLUMES   -> apaga os dados gravados no banco.",
        "",
        "O que NAO e apagado: o codigo, o .env, o seed.sql e o arquivo baixado do",
        "Banco Central. Tudo isso continua no disco.",
    )

    aviso("a etapa 1 para o ambiente; voce pode subir de novo sem perder dados.")
    if not confirmar("Executar a etapa 1 (parar os containers)?", padrao_sim=False):
        ok("nada foi feito: o ambiente continua como estava.")
        return

    certo, _ = rodar(["docker", "compose", "down"],
                     "parar e remover os containers do PostgreSQL/API",
                     dica_se_falhar="se o container nao existir, isso e normal: nada a parar.")
    if ARQ_COMPOSE_MYSQL.exists():
        rodar(comando_compose("mysql") + ["down"],
              "parar e remover o container do MySQL (se existir)")

    if not certo:
        erro("a desinstalacao nao terminou.")
        return
    ok("containers removidos.")

    explicar(
        "",
        "Os dados continuam no volume. Subir de novo traz o banco como estava.",
    )
    aviso("a etapa 2 e IRREVERSIVEL: apaga os dados do banco.")
    o_que_fazer("se quiser guardar os dados, copie antes com pg_dump.")
    if not confirmar("Apagar TAMBEM os dados (remover os volumes)?", padrao_sim=False):
        ok("dados preservados no volume.")
        return

    certo, _ = rodar(["docker", "compose", "down", "-v"],
                     "remover os volumes (apaga os dados do banco)",
                     dica_se_falhar="o volume pode ja ter sido removido; confira com 'docker volume ls'.")
    if ARQ_COMPOSE_MYSQL.exists():
        rodar(comando_compose("mysql") + ["down", "-v"], "remover o volume do MySQL")
    if certo:
        ok("dados apagados. Para recomecar: python instalar.py e escolha a opcao 8.")
    else:
        erro("nao consegui remover os volumes.")
        o_que_fazer("confira os volumes com: docker volume ls")


# ===========================================================================
# 15. Menu
# ===========================================================================

OPCOES = [
    ("1", "Verificar os pre-requisitos do ambiente atual"),
    ("2", "Criar/atualizar o arquivo .env"),
    ("3", "Escolher o ambiente (Docker local ou Neon)"),
    ("4", "Preparar o banco (Docker: subir container | Neon: testar conexao)"),
    ("5", "Criar a tabela e carregar os dados (init + seed)"),
    ("6", "Subir a API (Docker: container | Neon: Uvicorn local)"),
    ("7", "Testar os 3 endpoints"),
    ("8", "Instalar tudo na ordem (2 a 7)"),
    ("9", "Desinstalar / parar o ambiente"),
    ("0", "Sair"),
]


def mostrar_menu() -> None:
    """Imprime o menu com uma linha de explicacao em cada opcao."""
    titulo("Instalador do Termometro (Degrau 1)")
    explicar(
        "Escolha o numero da acao. Cada acao diz o motivo e confere o que precisa",
        "antes de agir.",
        "Ambiente: " + AMBIENTES[ambiente_atual()] + " | Banco: " + banco_atual(),
    )
    print("")
    for numero, descricao in OPCOES:
        print("  " + numero + ") " + descricao)


def main() -> int:
    """Loop do menu. Devolve 0 ao sair normalmente."""
    acoes = {
        "1": lambda: verificar_pre_requisitos(),
        "2": lambda: criar_env(),
        "3": lambda: escolher_ambiente() and True,
        "4": lambda: preparar_banco(),
        "5": lambda: carregar_dados(),
        "6": lambda: subir_api(),
        "7": lambda: testar_endpoints(),
        "8": lambda: instalar_tudo(),
        "9": lambda: desinstalar(),
    }

    while True:
        mostrar_menu()
        escolha = perguntar_opcao("Opcao", tuple(numero for numero, _ in OPCOES), "0")

        if escolha == "0":
            print("")
            print("  Ate logo. Para voltar: python instalar.py")
            return 0

        acao = acoes.get(escolha)
        if acao is None:
            # Defesa extra: se o menu ganhar uma opcao e o dicionario nao,
            # isto avisa em vez de estourar KeyError.
            erro("a opcao " + escolha + " aparece no menu, mas nao tem acao ligada.")
            o_que_fazer("isto e um defeito do instalador; avise o dono do projeto.")
            continue

        print("")
        print("  >>> executando a opcao " + escolha + " ...")
        acao()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("")
        print("  [aviso] interrompido pelo usuario (Ctrl+C). Nada foi desfeito.")
        sys.exit(130)
    except Exception as falha:  # noqa: BLE001 - rede de seguranca final
        # Rede de seguranca: qualquer erro nao previsto vira mensagem legivel,
        # em vez de um monte de linhas de rastreamento que ninguem entende.
        print("")
        print("  [erro] aconteceu um problema nao previsto: " + type(falha).__name__)
        print("         detalhe: " + str(falha))
        print("         -> copie esta mensagem e avise o dono do projeto.")
        sys.exit(1)
