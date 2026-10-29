#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""main.py — ponto de entrada: cria a aplicação FastAPI e liga as rotas.

É a única peça que o servidor (Uvicorn) precisa conhecer: `uvicorn app.main:app`
significa "no módulo app/main.py, use o objeto `app`".
"""

from fastapi import FastAPI

from .routes import router

app = FastAPI(
    title="Termometro — IPCA",
    version="1.0.0",
    description=(
        "API de leitura da serie historica do IPCA (SGS 433, Banco Central) "
        "guardada em PostgreSQL. Degrau 1 da trilha."
    ),
)

app.include_router(router)
