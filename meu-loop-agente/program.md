# Loop Program — redução do bundle inicial (exemplo com Next.js)

> Este arquivo é o CONTRATO do agente. Só o humano altera.
> Os números ficam em `baseline.json`; comandos e medição, em `config_loop.json`.
> Mantenha os três coerentes entre si.

# Contrato do Loop — Termômetro (Degrau 1)

## Objetivo
Construir uma API que consulta a série histórica do IPCA (SGS 433, Banco Central) armazenada em PostgreSQL rodando em Docker.

## Métrica principal
Número de endpoints funcionando corretamente na verificação manual.
- Baseline: 0
- Meta do degrau: 3 (/health, /ipca/ultimo, /ipca/serie)

## Limites (o que o agente NÃO pode fazer neste degrau)
- Não criar front-end.
- Não criar testes automatizados.
- Não configurar CI/CD.
- Não usar MongoDB nem Redis.
- Não fazer deploy em servidor.
- Não usar código de outros projetos (api-cep-valida, bot-indicadores).
- Só atuar dentro de `workspace/`.

## Critérios de aceite do Degrau 1
1. Repositório público `ipca-postgres-docker`.
2. `docker-compose.yml` sobe PostgreSQL com um comando.
3. Tabela `ipca` criada e populada (dados reais + fictícios).
4. Scripts SQL versionados em `workspace/db/`.
5. API responde em /health, /ipca/ultimo e /ipca/serie.
6. Ciclo registrado em `log.md` com decisão ACEITO.
7. README explica o projeto e onde a técnica aparece no projeto final.

## Regra de iteração
Cada ciclo: hipótese → UMA mudança pequena → teste → medição → decisão → registro no log.