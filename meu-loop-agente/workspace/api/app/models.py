#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""models.py — as consultas SQL da tabela `ipca`, escritas à mão.

Escolha do projeto: SQL direto, sem ORM (Object-Relational Mapper, camada que
traduz objeto Python em SQL). Motivo: o Degrau 1 existe para aprender modelagem
relacional — com ORM, o `SELECT ... ORDER BY data DESC LIMIT 1` viraria
`query.order_by(...).first()` e o SQL, que é o assunto da aula, desapareceria.

Cada função recebe a conexão por parâmetro: quem abre e fecha é o `database.py`.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

# Os três tipos aceitos pelo CHECK da tabela. A API valida aqui para responder
# 422 (pedido inválido) em vez de devolver lista vazia e deixar o usuário confuso.
TIPOS_VALIDOS = ("real", "ficticio")

SQL_ULTIMO = """
    SELECT data, valor, tipo
    FROM ipca
    ORDER BY data DESC
    LIMIT 1;
"""

SQL_SERIE = """
    SELECT data, valor, tipo
    FROM ipca
    {filtro}
    ORDER BY data ASC;
"""

SQL_VERSAO = "SELECT version();"


@dataclass
class RegistroIpca:
    """Uma linha da tabela, já convertida para tipos que viram JSON."""

    data: date
    valor: Decimal
    tipo: str

    def para_dicionario(self) -> dict:
        """Formato de saída da API: data em ISO (aaaa-mm-dd) e valor numérico."""
        return {
            "data": self.data.isoformat(),
            "valor": float(self.valor),
            "tipo": self.tipo,
        }


def _linha_para_registro(linha) -> RegistroIpca:
    """Traduz uma linha do cursor (tupla) no objeto RegistroIpca."""
    data, valor, tipo = linha
    return RegistroIpca(data=data, valor=valor, tipo=tipo)


def buscar_ultimo(conn) -> Optional[RegistroIpca]:
    """Devolve o registro com a maior data, ou None se a tabela estiver vazia.

    Atenção: os dois registros fictícios de 2099 são, por definição, os "mais
    recentes". Isso é intencional — é o teste de que a ordenação funciona.
    """
    with conn.cursor() as cursor:
        cursor.execute(SQL_ULTIMO)
        linha = cursor.fetchone()
    return _linha_para_registro(linha) if linha else None


def listar_serie(conn, tipo: Optional[str] = None) -> list:
    """Devolve a série em ordem crescente de data, opcionalmente filtrada por tipo."""
    filtro = "" if tipo is None else "WHERE tipo = %s"
    parametros = () if tipo is None else (tipo,)
    with conn.cursor() as cursor:
        cursor.execute(SQL_SERIE.format(filtro=filtro), parametros)
        linhas = cursor.fetchall()
    return [_linha_para_registro(linha) for linha in linhas]


def versao_do_postgres(conn) -> str:
    """Devolve a versão do servidor — prova de que a conexão é real, não decorada."""
    with conn.cursor() as cursor:
        cursor.execute(SQL_VERSAO)
        linha = cursor.fetchone()
    return linha[0] if linha else "desconhecida"
