#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gerar_seed.py — transforma o raw do IPCA em seed.sql pronto para rodar.

O que faz:
  - le data/raw/ipca_433.json (o que baixar_dados.py gravou);
  - converte a data de dd/mm/aaaa (formato do Banco Central) para aaaa-mm-dd,
    que e o formato que o PostgreSQL entende como DATE;
  - acrescenta DUAS linhas ficticias, com data no ano 2099;
  - escreve meu-loop-agente/workspace/db/seed.sql.

Por que existe:
  - separa "baixar o dado" de "montar o SQL". O raw continua intocado, e a seed
    pode ser regerada quantas vezes for preciso a partir da mesma foto.

Uso:
  python meu-loop-agente/workspace/scripts/gerar_seed.py

Sem emojis de proposito: compatibilidade com o console do Windows.
"""

import argparse
import json
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

RAIZ_DO_PROJETO = Path(__file__).resolve().parents[3]
ARQ_RAW = RAIZ_DO_PROJETO / "data" / "raw" / "ipca_433.json"
ARQ_SEED = (
    RAIZ_DO_PROJETO / "meu-loop-agente" / "workspace" / "db" / "seed.sql"
)

# As duas linhas inventadas. O ano 2099 e proposital: fica no fim da linha do
# tempo, longe da serie real, e salta aos olhos em qualquer consulta ordenada
# por data. Dado de teste misturado no meio do dado real engana a leitura.
FICTICIOS = [
    ("2099-01-01", Decimal("1.2345")),
    ("2099-02-01", Decimal("2.3456")),
]


def converter_data(texto: str) -> str:
    """Converte '01/01/1980' (Banco Central) em '1980-01-01' (PostgreSQL).

    Levanta ValueError com mensagem clara quando o formato nao bate, para nao
    gravar uma data torta no banco sem ninguem perceber.
    """
    try:
        return datetime.strptime(texto, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("data em formato inesperado: " + repr(texto))


def converter_valor(texto: str) -> Decimal:
    """Converte '0.42' em Decimal ('0.42'), sem passar por ponto flutuante.

    O Banco Central manda o numero como texto. Virar Decimal direto preserva
    as casas decimais exatas; passar por float introduziria ruido binario.
    """
    try:
        return Decimal(str(texto).replace(",", "."))
    except InvalidOperation:
        raise ValueError("valor em formato inesperado: " + repr(texto))


def montar_linhas(registros: list) -> tuple:
    """Devolve (linhas_reais, ignorados) a partir do JSON do Banco Central."""
    reais = []
    ignorados = 0
    for registro in registros:
        try:
            data = converter_data(registro["data"])
            valor = converter_valor(registro["valor"])
        except (KeyError, ValueError, TypeError):
            ignorados += 1
            continue
        reais.append((data, valor, "real"))
    return reais, ignorados


def escrever_seed(linhas: list, dialeto: str = "postgres") -> None:
    """Grava o arquivo SQL com um unico INSERT e a traducao do "nao duplique".

    O comando que ignora linha repetida muda de nome conforme o banco:
    - PostgreSQL: `ON CONFLICT (data) DO NOTHING`
    - MySQL: `ON DUPLICATE KEY UPDATE data = data` (atualizar a data para ela
      mesma nao muda nada, e e o jeito do MySQL de dizer "ja existe, ignore")
    """
    if dialeto == "mysql":
        final = "ON DUPLICATE KEY UPDATE data = data;"
        explicacao = (
            "-- ON DUPLICATE KEY UPDATE data = data: se o mes ja existe, a linha e",
            '-- ignorada em vez de dar erro (o jeito do MySQL de dizer "ja existe").',
        )
    else:
        final = "ON CONFLICT (data) DO NOTHING;"
        explicacao = (
            "-- ON CONFLICT (data) DO NOTHING: se o mes ja existe, a linha e ignorada",
            "-- em vez de dar erro. Assim rodar este arquivo duas vezes nao duplica",
            "-- nada e nao derruba a carga no meio.",
        )

    partes = [
        "-- Seed da tabela ipca, gerado por workspace/scripts/gerar_seed.py.",
        "-- Dialeto: " + dialeto + ". Nao edite a mao: rode o script de novo se o raw mudar.",
        "--",
    ]
    partes.extend(explicacao)
    partes.extend([
        "",
        "BEGIN;",
        "",
        "INSERT INTO ipca (data, valor, tipo) VALUES",
    ])

    valores = ['    (%s, %s, %s)' % (
        "'" + data + "'",
        str(valor.quantize(Decimal("0.0001"))),
        "'" + tipo + "'",
    ) for data, valor, tipo in linhas]

    corpo = ",\n".join(valores)
    partes.append(corpo)
    partes.append(final)
    partes.append("")
    partes.append("COMMIT;")
    partes.append("")

    ARQ_SEED.parent.mkdir(parents=True, exist_ok=True)
    ARQ_SEED.write_text("\n".join(partes), encoding="utf-8")


def main() -> int:
    """Le o raw, monta a seed e grava seed.sql. Devolve 0 quando tudo correu bem."""
    parser = argparse.ArgumentParser(
        description="Gera o seed.sql a partir do raw do Banco Central."
    )
    parser.add_argument(
        "--dialeto",
        choices=["postgres", "mysql"],
        default="postgres",
        help="Banco de destino: postgres (padrao) ou mysql.",
    )
    argumentos = parser.parse_args()

    if not ARQ_RAW.exists():
        print("[erro] nao encontrei " + str(ARQ_RAW.relative_to(RAIZ_DO_PROJETO)) + ".")
        print("       Rode primeiro: python meu-loop-agente/workspace/scripts/baixar_dados.py")
        return 1

    try:
        registros = json.loads(ARQ_RAW.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erro:
        print("[erro] o raw nao e um JSON valido (linha " + str(erro.lineno) + ").")
        print("       O arquivo pode ter sido editado a mao; baixe de novo.")
        return 1

    if not isinstance(registros, list) or not registros:
        print("[erro] o raw nao tem uma lista de registros. Baixe de novo.")
        return 1

    reais, ignorados = montar_linhas(registros)
    if not reais:
        print("[erro] nenhum registro pode ser convertido; nada seria inserido.")
        return 1

    # Ficticios entram no fim da lista para ficarem legiveis no arquivo gerado.
    linhas = reais + [(data, valor, "ficticio") for data, valor in FICTICIOS]
    escrever_seed(linhas, argumentos.dialeto)

    print("[ok] " + str(ARQ_SEED.relative_to(RAIZ_DO_PROJETO))
          + " gerado (dialeto " + argumentos.dialeto + ")")
    print("     linhas totais   : " + str(len(linhas)))
    print("     linhas reais    : " + str(len(reais)))
    print("     linhas ficticias: " + str(len(FICTICIOS)) + " (ano 2099)")
    print("     linhas ignoradas: " + str(ignorados))
    if reais:
        print("     periodo         : " + reais[0][0] + " a " + reais[-1][0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
