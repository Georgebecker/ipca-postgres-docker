-- Verificacao manual do Degrau 1 (sem testes automatizados, por escopo).
-- Rode uma consulta por vez e compare com o "esperado" no comentario.
-- As quatro respostas foram conferidas contra o seed gerado do raw de 29/10/2026.

-- 1) Quantas linhas existem na tabela?
-- Esperado: 563  (561 meses reais + 2 ficticios)
SELECT COUNT(*) AS total FROM ipca;

-- 2) Quantas linhas de cada tipo?
-- Esperado: ficticio = 2 | real = 561
SELECT tipo, COUNT(*) AS quantidade
FROM ipca
GROUP BY tipo
ORDER BY tipo;

-- 3) Os cinco meses mais recentes, do mais novo para o mais antigo.
-- Esperado:
--   2099-02-01 | 2.3456 | ficticio
--   2099-01-01 | 1.2345 | ficticio
--   2026-09-01 | 0.8200 | real
--   2026-08-01 | -0.3200 | real
--   2026-07-01 | 0.0700 | real
SELECT data, valor, tipo
FROM ipca
ORDER BY data DESC
LIMIT 5;

-- 4) Quais indices existem na tabela?
-- Esperado: idx_ipca_data_desc (o que criamos), ipca_data_key (UNIQUE em data)
--           e ipca_pkey (chave primaria em id).
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'ipca'
ORDER BY indexname;
