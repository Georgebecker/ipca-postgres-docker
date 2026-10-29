#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""config.py — reúne as configurações da API em um único lugar.

Problema que resolve: espalhar `os.getenv("POSTGRES_USER")` pelo código faz cada
arquivo conhecer o nome da variável, e um erro de digitação vira `None` silencioso
(o programa roda, mas conecta em lugar nenhum). Aqui o ambiente é lido UMA vez,
validado e entregue pronto.

Analogia: é o crachá de acesso na portaria. O prédio inteiro confia no crachá já
conferido na entrada; nenhum setor precisa ligar para o RH perguntar quem é você.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Este arquivo vive em workspace/api/app/, então subir quatro pastas chega na raiz
# do projeto: app -> api -> workspace -> meu-loop-agente -> raiz.
RAIZ_DO_PROJETO = Path(__file__).resolve().parents[4]
ARQ_ENV = RAIZ_DO_PROJETO / ".env"


class Configuracoes(BaseSettings):
    """Configuração da API, carregada do `.env` ou das variáveis de ambiente.

    Dentro do container não existe arquivo `.env` (ele nunca é copiado para a
    imagem); nesse caso o pydantic-settings cai nas variáveis de ambiente, que o
    docker-compose injeta. O mesmo código serve para os dois cenários.
    """

    model_config = SettingsConfigDict(
        env_file=str(ARQ_ENV) if ARQ_ENV.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Sem valor padrão de propósito: se faltar no ambiente, a API para na largada
    # com mensagem clara, em vez de tentar conectar em um banco inexistente.
    postgres_user: str
    postgres_password: str
    postgres_db: str

    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @property
    def parametros_conexao(self) -> dict:
        """Devolve os parâmetros que o psycopg2 espera, sem montar string de DSN.

        Passar dicionário evita o clássico problema de senha com `@` ou `:` que
        quebra uma URL de conexão.
        """
        return {
            "host": self.postgres_host,
            "port": self.postgres_port,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "dbname": self.postgres_db,
        }


_configuracoes = None


def obter_configuracoes() -> Configuracoes:
    """Devolve a configuração já validada, criando-a só na primeira chamada."""
    global _configuracoes
    if _configuracoes is None:
        _configuracoes = Configuracoes()
    return _configuracoes
