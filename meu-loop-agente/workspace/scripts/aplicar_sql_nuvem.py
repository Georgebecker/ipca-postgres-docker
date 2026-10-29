#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""aplicar_sql_nuvem.py — aplica init.sql e seed.sql direto no banco da nuvem.

(1) O que é: um script que envia os arquivos SQL do projeto para o PostgreSQL do
    Neon, sem passar por Docker nem por `psql` de container.
(2) Para que serve: com o banco fora da máquina, não existe container onde entrar
    e rodar `psql`. Este script faz o mesmo trabalho usando a URL de conexão que
    está no `.env`, na variável DATABASE_URL.
(3) Comparação: no modo Docker, você entrava na cozinha do restaurante (o
    container) para preparar o prato. Aqui o restaurante é na nuvem: você manda o
    pedido pela porta da frente (a URL de conexão) e não precisa entrar lá.

Como o SQL é enviado:
- se a biblioteca `psycopg2` estiver instalada, ela abre a conexão e executa;
- se não estiver, o script usa o CLI do Neon (`neon psql`), que já faz o mesmo.
  Assim funciona nas duas situações, sem obrigar instalação extra.

Uso:
    python meu-loop-agente/workspace/scripts/aplicar_sql_nuvem.py
    python meu-loop-agente/workspace/scripts/aplicar_sql_nuvem.py --somente init
    python meu-loop-agente/workspace/scripts/aplicar_sql_nuvem.py --somente seed

Os dois arquivos são idempotentes: rodar duas vezes não duplica nada.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Este arquivo vive em <raiz>/meu-loop-agente/workspace/scripts/, então subir
# três pastas chega na raiz do projeto.
RAIZ = Path(__file__).resolve().parents[3]
ARQ_ENV = RAIZ / ".env"
DB = RAIZ / "meu-loop-agente" / "workspace" / "db"
ARQ_INIT = DB / "init.sql"
ARQ_SEED = DB / "seed.sql"
ARQ_RAW = RAIZ / "data" / "raw" / "ipca_433.json"
SCRIPT_GERAR_SEED = RAIZ / "meu-loop-agente" / "workspace" / "scripts" / "gerar_seed.py"


def titulo(texto: str) -> None:
    print("")
    print("=" * 64)
    print(texto)
    print("=" * 64)


def ok(mensagem: str) -> None:
    print("  [ok] " + mensagem)


def aviso(mensagem: str) -> None:
    print("  [aviso] " + mensagem)


def erro(mensagem: str) -> None:
    print("  [erro] " + mensagem)


def o_que_fazer(*linhas: str) -> None:
    for linha in linhas:
        print("         -> " + linha)


def ler_env() -> dict:
    """Lê o `.env` da raiz e devolve chave -> valor.

    Leitura própria (em vez de python-dotenv) porque este script deve rodar mesmo
    com o Python "cru", sem nenhuma biblioteca instalada.

    Detalhe que já causou erro: o `neon init` grava valores entre aspas, como
    DATABASE_URL="postgresql://...". As aspas NÃO fazem parte do valor — se
    ficarem, a URL começa com aspas e o banco recusa a conexão. Por isso elas
    são removidas aqui.
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


def obter_url() -> str:
    """Devolve a DATABASE_URL pronta para o psycopg2.

    Dois ajustes que evitam erro na conexão:
    1. `postgresql+psycopg2://` é sintaxe do SQLAlchemy, não do psycopg2 puro —
       se a URL vier assim, o sufixo é removido (este projeto não usa ORM).
    2. O Neon exige conexão criptografada; se faltar `sslmode`, ele é acrescentado.
    """
    url = ler_env().get("DATABASE_URL", "").strip()
    if not url:
        erro("nao encontrei DATABASE_URL no arquivo .env.")
        o_que_fazer("rode: neon init   (ou copie a connection string do console do Neon",
                    "e cole em DATABASE_URL=... no .env)")
        raise SystemExit(1)

    for prefixo in ("postgresql+psycopg2://", "postgres+psycopg2://"):
        if url.startswith(prefixo):
            url = "postgresql://" + url.split("://", 1)[1]
            break

    if "sslmode=" in url:
        return url
    return url + ("&" if "?" in url else "?") + "sslmode=require"


def executar_com_psycopg2(url: str, arquivo: Path) -> bool:
    """Aplica o arquivo SQL usando a biblioteca psycopg2. Devolve se deu certo."""
    import psycopg2  # importado aqui dentro: só é necessário neste caminho

    print("  # enviando " + arquivo.name + " via psycopg2")
    sql = arquivo.read_text(encoding="utf-8")
    try:
        with psycopg2.connect(url) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute(sql)
        return True
    except psycopg2.Error as falha:
        erro("o banco recusou o SQL de " + arquivo.name + ":")
        print("         " + str(falha).strip().splitlines()[0])
        return False


def executar_com_neon_psql(arquivo: Path) -> bool:
    """Aplica o arquivo SQL usando o CLI do Neon. Devolve se deu certo.

    Caminho alternativo para quando a psycopg2 não está instalada. O CLI já sabe
    onde está o banco (ele guardou as credenciais no login e no `.neon`).
    """
    if shutil.which("neon") is None:
        erro("nem psycopg2 nem o CLI do Neon estao disponiveis.")
        o_que_fazer("instale uma das duas opcoes:",
                    "  pip install psycopg2-binary",
                    "  npm i -g neon")
        return False

    print("  # enviando " + arquivo.name + " via 'neon psql'")
    resultado = subprocess.run(
        "neon psql",
        cwd=str(RAIZ),
        shell=True,
        input=arquivo.read_bytes(),
        capture_output=True,
        timeout=600,
    )
    if resultado.returncode != 0:
        saida = (resultado.stderr or b"").decode("utf-8", "replace").strip()
        erro("o 'neon psql' terminou com codigo " + str(resultado.returncode) + ".")
        for linha in saida.splitlines()[-4:]:
            print("         " + linha)
        return False
    return True


def aplicar(arquivo: Path, url: str) -> bool:
    """Escolhe o transporte disponível e aplica o arquivo."""
    if not arquivo.exists():
        erro("nao encontrei " + str(arquivo.relative_to(RAIZ)) + ".")
        return False

    try:
        import psycopg2  # noqa: F401 - só para saber se está disponível
        disponivel = True
    except ImportError:
        disponivel = False
        aviso("psycopg2 nao instalada; vou usar o CLI do Neon como alternativa.")

    if disponivel:
        return executar_com_psycopg2(url, arquivo)
    return executar_com_neon_psql(arquivo)


def conferir(url: str) -> None:
    """Mostra a contagem final, para provar que os dados entraram."""
    try:
        import psycopg2
    except ImportError:
        print("")
        print("  # conferencia (via neon psql)")
        subprocess.run(
            "neon psql",
            cwd=str(RAIZ),
            shell=True,
            input=b"SELECT tipo, COUNT(*) AS quantidade FROM ipca GROUP BY tipo ORDER BY tipo;\n",
            timeout=300,
        )
        return

    print("")
    print("  # conferencia: quantas linhas por tipo")
    try:
        with psycopg2.connect(url) as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("SELECT tipo, COUNT(*) FROM ipca GROUP BY tipo ORDER BY tipo;")
                for tipo, quantidade in cursor.fetchall():
                    print("    " + str(tipo) + ": " + str(quantidade))
    except psycopg2.Error as falha:
        erro("nao consegui conferir a contagem: " + str(falha).strip().splitlines()[0])


def main() -> int:
    """Aplica init e/ou seed no banco da nuvem. Devolve 0 quando tudo deu certo."""
    parser = argparse.ArgumentParser(
        description="Aplica init.sql e seed.sql no PostgreSQL da nuvem (Neon)."
    )
    parser.add_argument(
        "--somente",
        choices=["init", "seed"],
        default=None,
        help="Aplica apenas um dos arquivos (padrao: os dois, init antes do seed).",
    )
    argumentos = parser.parse_args()

    titulo("Aplicando SQL no banco da nuvem")
    print("  Motivo: com o banco fora da maquina nao existe container para entrar;")
    print("  o envio e feito pela URL de conexao (DATABASE_URL).")

    url = obter_url()
    ok("DATABASE_URL encontrada no .env (valor nao exibido)")

    if argumentos.somente != "seed":
        titulo("1) Estrutura (init.sql)")
        print("  Cria a tabela ipca e o indice. Usa IF NOT EXISTS: rodar de novo nao quebra.")
        if not aplicar(ARQ_INIT, url):
            return 1
        ok("init.sql aplicado")

    if argumentos.somente != "init":
        titulo("2) Dados (seed.sql)")
        if not ARQ_SEED.exists():
            aviso("seed.sql nao existe; vou gerar a partir do raw.")
            if not ARQ_RAW.exists():
                aviso("o raw tambem nao existe; baixando do Banco Central.")
                subprocess.run([sys.executable,
                                str(RAIZ / "meu-loop-agente/workspace/scripts/baixar_dados.py")],
                               cwd=str(RAIZ))
            subprocess.run([sys.executable, str(SCRIPT_GERAR_SEED), "--dialeto", "postgres"],
                           cwd=str(RAIZ))
        print("  Insere os 561 meses reais + 2 ficticios. Mes ja existente e ignorado.")
        if not aplicar(ARQ_SEED, url):
            return 1
        ok("seed.sql aplicado")

    conferir(url)

    print("")
    ok("concluido. O banco da nuvem esta com a estrutura e os dados do projeto.")
    o_que_fazer("para subir a API: veja a secao 'Rodar a API sem Docker' no README")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("")
        print("  [aviso] interrompido pelo usuario.")
        sys.exit(130)
