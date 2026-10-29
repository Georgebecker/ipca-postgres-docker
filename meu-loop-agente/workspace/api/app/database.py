#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""database.py — mantém um conjunto de conexões abertas com o PostgreSQL.

Problema que resolve: abrir uma conexão nova a cada requisição custa caro (aperto
de mão, autenticação, memória). Um *pool* é a fila do caixa do banco: as conexões
ficam prontas e cada requisição usa uma por alguns milissegundos, devolvendo depois.

Por que ThreadedConnectionPool: o Uvicorn atende requisições em várias threads.
Um pool sem proteção entregaria a MESMA conexão para duas requisições ao mesmo
tempo — e uma delas leria a resposta da outra.
"""

from contextlib import contextmanager

from psycopg2.pool import ThreadedConnectionPool

from .config import obter_configuracoes

# O pool é criado na primeira necessidade e reaproveitado até o processo morrer.
_pool = None


def obter_pool() -> ThreadedConnectionPool:
    """Cria (uma vez) e devolve o pool de conexões."""
    global _pool
    if _pool is None:
        parametros = obter_configuracoes().parametros_conexao
        _pool = ThreadedConnectionPool(minconn=1, maxconn=5, **parametros)
    return _pool


@contextmanager
def conexao():
    """Entrega uma conexão do pool e a devolve no fim, mesmo se der erro.

    O `with` garante a devolução: sem ele, uma exceção no meio deixaria a conexão
    presa e, depois de cinco erros, a API travaria por falta de conexão livre.
    """
    pool = obter_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)
