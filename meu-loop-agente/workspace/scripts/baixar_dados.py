#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""baixar_dados.py — baixa a serie historica do IPCA (SGS 433) do Banco Central.

O que faz:
  - pede ao Banco Central a serie 433 (IPCA mensal) em JSON;
  - grava a resposta, exatamente como veio, em data/raw/ipca_433.json.

Por que existe:
  - o dado oficial precisa entrar no projeto por um caminho repetivel. Baixar a
    planilha a mao nao deixa rastro de quando, de onde e de que tamanho veio.

Regra da pasta raw:
  - data/raw/ e o "original de cartorio": nao se edita, nao se "conserta".
  - se o arquivo ja existe, o script nao sobrescreve: avisa e para.
    Isso evita perder o dia da coleta original. Use --forcar quando quiser
    de proposito buscar de novo.

Uso:
  python meu-loop-agente/workspace/scripts/baixar_dados.py
  python meu-loop-agente/workspace/scripts/baixar_dados.py --forcar

Sem emojis de proposito: compatibilidade com o console do Windows.
"""

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

# A serie 433 e o IPCA mensal. Sem dataInicial, o Banco Central devolve a serie
# inteira (de 1980 ate o ultimo mes fechado) — e o que queremos: historico completo.
URL_SGS_433 = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"

# O script vive em <raiz>/meu-loop-agente/workspace/scripts/, entao subir tres
# pastas chega na raiz do projeto. parents[0] seria a propria pasta scripts.
RAIZ_DO_PROJETO = Path(__file__).resolve().parents[3]
ARQ_RAW = RAIZ_DO_PROJETO / "data" / "raw" / "ipca_433.json"

TEMPO_LIMITE_SEGUNDOS = 60


def baixar(url: str) -> bytes:
    """Devolve o corpo da resposta da URL, em bytes.

    Existe separado do resto para deixar claro o unico ponto que toca a internet:
    se der erro de rede, e aqui que a mensagem aparece.
    """
    pedido = urllib.request.Request(
        url,
        headers={"User-Agent": "ipca-postgres-docker/1.0 (projeto de estudo)"},
    )
    with urllib.request.urlopen(pedido, timeout=TEMPO_LIMITE_SEGUNDOS) as resposta:
        return resposta.read()


def main() -> int:
    """Baixa a serie e grava o raw. Devolve 0 quando tudo correu bem."""
    parser = argparse.ArgumentParser(
        description="Baixa a serie 433 (IPCA) do Banco Central para data/raw/."
    )
    parser.add_argument(
        "--forcar",
        action="store_true",
        help="sobrescreve o raw existente (use so quando quiser recoletar)",
    )
    argumentos = parser.parse_args()

    if ARQ_RAW.exists() and not argumentos.forcar:
        print("[aviso] o arquivo ja existe: " + str(ARQ_RAW.relative_to(RAIZ_DO_PROJETO)))
        print("        A pasta data/raw/ guarda o original e nao deve ser reescrita.")
        print("        Se quiser buscar de novo de proposito, rode com --forcar.")
        return 1

    print("[info] baixando a serie 433 do Banco Central...")
    try:
        conteudo = baixar(URL_SGS_433)
    except urllib.error.HTTPError as erro:
        print("[erro] o Banco Central respondeu com erro HTTP " + str(erro.code) + ".")
        print("       Tente de novo em alguns minutos; a API costuma oscilar.")
        return 1
    except urllib.error.URLError as erro:
        print("[erro] nao consegui falar com o Banco Central: " + str(erro.reason) + ".")
        print("       Verifique a conexao com a internet e se ha proxy bloqueando.")
        return 1
    except TimeoutError:
        print("[erro] o Banco Central demorou mais de " + str(TEMPO_LIMITE_SEGUNDOS) + "s.")
        return 1

    if not conteudo.strip():
        print("[erro] a resposta veio vazia; nada foi gravado.")
        return 1

    # Grava os bytes recebidos sem traduzir nem reformatar: o raw tem que ser
    # a fotografia fiel do que o Banco Central entregou.
    ARQ_RAW.parent.mkdir(parents=True, exist_ok=True)
    ARQ_RAW.write_bytes(conteudo)

    tamanho_kb = len(conteudo) / 1024
    print("[ok] gravado " + str(ARQ_RAW.relative_to(RAIZ_DO_PROJETO))
          + " (" + format(tamanho_kb, ".1f") + " kB)")
    print("     Proximo passo: python meu-loop-agente/workspace/scripts/gerar_seed.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
