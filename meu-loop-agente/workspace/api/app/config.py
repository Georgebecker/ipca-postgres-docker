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
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Este arquivo vive em workspace/api/app/, então subir quatro pastas chega na raiz
# do projeto: app -> api -> workspace -> meu-loop-agente -> raiz.
RAIZ_DO_PROJETO = Path(__file__).resolve().parents[4]
ARQ_ENV = RAIZ_DO_PROJETO / ".env"


class Configuracoes(BaseSettings):
    """Configuração da API, carregada do `.env` ou das variáveis de ambiente.

    Duas formas de dizer onde está o banco, nesta ordem de preferência:

    1. **DATABASE_URL** — uma única linha com tudo (usuário, senha, host, porta e
       nome do banco). É o formato que o Neon entrega; também é o formato usado
       por quase todo serviço de banco na nuvem.
    2. **POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB / POSTGRES_HOST / PORT** —
       as peças separadas, usadas pelo PostgreSQL em Docker (`docker-compose.yml`).

    O código prefere a URL quando ela existe e cai nas peças quando não existe.
    Assim o mesmo projeto serve para banco local e para banco na nuvem, sem
    precisar editar código para trocar de ambiente.

    Dentro do container não existe arquivo `.env` (ele nunca é copiado para a
    imagem); nesse caso o pydantic-settings usa as variáveis de ambiente que o
    docker-compose injeta.
    """

    model_config = SettingsConfigDict(
        env_file=str(ARQ_ENV) if ARQ_ENV.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Caminho 1: uma URL completa (Neon, ou qualquer Postgres gerenciado).
    database_url: Optional[str] = None

    # Caminho 2: as peças separadas (Docker local). Agora são opcionais, porque
    # quem usa DATABASE_URL não precisa delas.
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None

    postgres_host: str = "localhost"
    postgres_port: int = 5432

    @model_validator(mode="after")
    def conferir_de_onde_vem_o_banco(self):
        """Falha na largada se nenhuma das duas formas estiver configurada.

        Motivo: sem isso, a API subiria "com sucesso" e só quebraria na primeira
        consulta, com um erro de conexão difícil de ligar à causa real.
        """
        if self.database_url:
            return self

        faltando = [
            nome for nome in ("postgres_user", "postgres_password", "postgres_db")
            if not getattr(self, nome)
        ]
        if faltando:
            raise ValueError(
                "configure DATABASE_URL (banco na nuvem) OU as variaveis "
                + ", ".join(faltando) + " no arquivo .env"
            )
        return self

    @property
    def usa_url(self) -> bool:
        """Diz qual das duas formas está em uso. Útil para mensagens de log."""
        return bool(self.database_url)

    @property
    def dsn(self) -> str:
        """Devolve a URL de conexão pronta, garantindo SSL quando é nuvem.

        Por que mexer no sslmode: o Neon exige conexão criptografada. Se a URL
        vier sem `sslmode`, a conexão é recusada com um erro que não explica
        nada. Acrescentar aqui evita essa armadilha.
        """
        url = self.database_url or ""
        if "sslmode=" in url:
            return url
        separador = "&" if "?" in url else "?"
        return url + separador + "sslmode=require"

    @property
    def parametros_conexao(self) -> dict:
        """Peças separadas que o psycopg2 espera (usado quando não há URL).

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
