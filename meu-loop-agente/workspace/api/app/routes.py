#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""routes.py — as três rotas (caminhos) que a API expõe.

Cada rota é uma "janela" do banco: /health diz se está tudo de pé, /ipca/ultimo
devolve o mês mais recente e /ipca/serie devolve a série inteira.

Erro de banco nunca sai como stack trace: vira resposta HTTP 503 com mensagem
curta, porque quem consome a API precisa saber que o problema é do servidor, não
do pedido dele.
"""

from typing import List, Literal, Optional

import psycopg2
from fastapi import APIRouter, HTTPException, Query

from . import models
from .database import conexao, descrever_origem

router = APIRouter()

# Mensagem única para falha de banco: evita vazar host, usuário ou senha na resposta.
ERRO_BANCO = "o banco de dados nao respondeu; verifique se o container do PostgreSQL esta de pe"


@router.get("/", include_in_schema=False)
def raiz() -> dict:
    """Página inicial: diz quais caminhos existem.

    Sem esta rota, abrir http://localhost:8000/ devolve `{"detail":"Not Found"}`,
    que parece defeito mas é só ausência de rota. Aqui ela responde a lista.
    """
    return {
        "api": "Termometro - IPCA (SGS 433)",
        "endpoints": ["/health", "/ipca/ultimo", "/ipca/serie"],
        "filtro_opcional": "/ipca/serie?tipo=real",
        "documentacao": "/docs",
    }


@router.get("/health")
def health() -> dict:
    """Prova de vida: responde só depois de perguntar a versão ao PostgreSQL.

    Retornar "ok" fixo seria mentira: a API poderia estar de pé com o banco morto.
    """
    try:
        with conexao() as conn:
            versao = models.versao_do_postgres(conn)
    except psycopg2.Error:
        raise HTTPException(
            status_code=503,
            detail={"status": "erro", "postgres": "indisponivel", "motivo": ERRO_BANCO},
        )

    # A versão completa termina com detalhes do sistema operacional; o primeiro
    # trecho ("PostgreSQL 16.x ...") já responde o que interessa.
    return {
        "status": "ok",
        "postgres": "ok",
        "versao_postgres": versao.split(" on ")[0],
        # Diz se a resposta veio do banco na nuvem ou do banco local. Sem isso,
        # comparar resultados de dois ambientes vira adivinhação.
        "origem": descrever_origem(),
    }


@router.get("/ipca/ultimo")
def ipca_ultimo() -> dict:
    """Devolve o registro de maior data (hoje, um dos fictícios de 2099)."""
    try:
        with conexao() as conn:
            registro = models.buscar_ultimo(conn)
    except psycopg2.Error:
        raise HTTPException(status_code=503, detail=ERRO_BANCO)

    if registro is None:
        # 404 é diferente de 503: aqui o banco respondeu, mas não há dado.
        raise HTTPException(status_code=404, detail="a tabela ipca esta vazia")
    return registro.para_dicionario()


@router.get("/ipca/serie", response_model=List[dict])
def ipca_serie(
    tipo: Optional[Literal["real", "ficticio"]] = Query(
        default=None,
        description="Filtra por origem do dado. Sem o parametro, devolve tudo.",
    )
) -> list:
    """Devolve a série em ordem crescente de data; `?tipo=` filtra a origem.

    O tipo é validado pelo próprio FastAPI: `?tipo=xyz` recebe 422 com a lista do
    que é aceito, antes de qualquer consulta ao banco.
    """
    try:
        with conexao() as conn:
            registros = models.listar_serie(conn, tipo)
    except psycopg2.Error:
        raise HTTPException(status_code=503, detail=ERRO_BANCO)
    return [registro.para_dicionario() for registro in registros]
