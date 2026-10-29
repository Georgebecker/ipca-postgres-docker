#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""medir_endpoints.py — conta quantos dos 3 endpoints da API respondem de verdade.

É o medidor do ciclo 2: o verificador do loop lê o número impresso aqui.
"Responder de verdade" = status HTTP 200 e corpo em JSON válido. Um endpoint que
devolve 500, 404 ou HTML de erro não conta.

Uso:
  python meu-loop-agente/workspace/scripts/medir_endpoints.py

Endereço da API: variavel de ambiente API_URL (padrao http://localhost:8000).

Sem emojis de proposito: compatibilidade com o console do Windows.
"""

import json
import os
import sys
import urllib.error
import urllib.request

URL_BASE = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
TEMPO_LIMITE_SEGUNDOS = 5

ENDPOINTS = [
    ("/health", "GET /health"),
    ("/ipca/ultimo", "GET /ipca/ultimo"),
    ("/ipca/serie", "GET /ipca/serie"),
]


def testar(caminho: str) -> tuple:
    """Devolve (ok, descricao). Nunca levanta excecao: falha conta como zero."""
    url = URL_BASE + caminho
    try:
        with urllib.request.urlopen(url, timeout=TEMPO_LIMITE_SEGUNDOS) as resposta:
            if resposta.status != 200:
                return False, "status " + str(resposta.status)
            corpo = resposta.read()
    except urllib.error.HTTPError as erro:
        return False, "status " + str(erro.code)
    except urllib.error.URLError as erro:
        return False, "sem conexao (" + str(erro.reason) + ")"
    except TimeoutError:
        return False, "tempo esgotado"

    try:
        json.loads(corpo)
    except json.JSONDecodeError:
        return False, "resposta nao e JSON"
    return True, "200 e JSON valido"


def main() -> int:
    """Testa os tres endpoints e imprime o total que passou."""
    print("[info] medindo a API em " + URL_BASE)
    aprovados = 0
    for caminho, rotulo in ENDPOINTS:
        ok, descricao = testar(caminho)
        print("  " + ("[ok]   " if ok else "[falha] ") + rotulo + " -> " + descricao)
        if ok:
            aprovados += 1

    print("")
    print("endpoints ok   : " + str(aprovados))
    print("endpoints total: " + str(len(ENDPOINTS)))

    if aprovados == 0:
        print("")
        print("A API nao respondeu. Suba o ambiente com: docker compose up -d")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
