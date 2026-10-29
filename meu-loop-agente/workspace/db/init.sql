-- Modelagem da serie historica do IPCA (SGS 433, Banco Central).
-- Este arquivo e executado pelo PostgreSQL na primeira subida do container
-- (pasta /docker-entrypoint-initdb.d), por isso nao ha CREATE DATABASE aqui:
-- o banco ja vem criado pela variavel POSTGRES_DB do docker-compose.

CREATE TABLE IF NOT EXISTS ipca (
    -- id: numero de ordem interno, gerado pelo banco. Nao e a "chave natural"
    -- da serie (essa e a data), mas evita depender de uma coluna de negocio
    -- como chave primaria.
    id        SERIAL PRIMARY KEY,

    -- data: competencia mensal do IPCA (mes de referencia do indice).
    -- UNIQUE impede carregar o mesmo mes duas vezes; NOT NULL porque uma linha
    -- sem data nao identifica nada.
    data      DATE NOT NULL UNIQUE,

    -- valor: variacao percentual do mes. NUMERIC (e nao FLOAT) porque numero
    -- decimal exato nao aceita erro de arredondamento binario: 0.42 tem que
    -- continuar 0.42, e nao 0.41999999999999998.
    valor     NUMERIC(10,4) NOT NULL,

    -- tipo: separa o dado oficial do dado inventado para teste.
    -- O CHECK funciona como porteiro: qualquer valor fora da lista e recusado
    -- pelo banco, nao pela aplicacao.
    tipo      VARCHAR(20) NOT NULL DEFAULT 'real'
              CHECK (tipo IN ('real', 'ficticio')),

    -- criado_em: data e hora da carga. Serve para auditar quando a linha entrou,
    -- sem precisar confiar no relogio de quem carregou.
    criado_em TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indice decrescente em data: as consultas do projeto pedem sempre "os meses
-- mais recentes primeiro". Com o indice, o banco le o fim da lista direto,
-- sem ordenar a tabela inteira toda vez.
CREATE INDEX IF NOT EXISTS idx_ipca_data_desc ON ipca (data DESC);
