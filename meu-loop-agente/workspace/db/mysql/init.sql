-- Modelagem da tabela ipca para MySQL 8 (o PostgreSQL tem o seu proprio init.sql).
-- Este arquivo e o "extra opcional": o projeto roda em PostgreSQL por padrao,
-- e esta versao existe para comparar os dois bancos lado a lado.

CREATE TABLE IF NOT EXISTS ipca (
    -- id: numero de ordem interno. AUTO_INCREMENT e o equivalente MySQL do SERIAL
    -- do PostgreSQL: "gere o proximo numero para mim".
    id        INT UNSIGNED NOT NULL AUTO_INCREMENT,

    -- data: competencia mensal (mes de referencia do indice).
    data      DATE NOT NULL,

    -- valor: variacao percentual do mes, com 4 casas decimais exatas.
    -- DECIMAL e o "NUMERIC" do MySQL; FLOAT teria erro de arredondamento binario.
    valor     DECIMAL(10,4) NOT NULL,

    -- tipo: separa dado oficial de dado inventado para teste.
    tipo      VARCHAR(20) NOT NULL DEFAULT 'real',

    -- criado_em: quando a linha entrou. CURRENT_TIMESTAMP e o NOW() do MySQL.
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- UNIQUE na data: o mesmo mes nao pode entrar duas vezes.
    UNIQUE KEY ipca_data_key (data),

    -- Indice decrescente: MySQL 8 aceita DESC de verdade (o 5.7 ignorava).
    KEY idx_ipca_data_desc (data DESC),

    -- CHECK: so entra 'real' ou 'ficticio'. MySQL passou a respeitar CHECK
    -- de verdade na versao 8.0.16; antes disso ele aceitava e fingia que nada
    -- tinha acontecido.
    CONSTRAINT ipca_tipo_check CHECK (tipo IN ('real', 'ficticio'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
