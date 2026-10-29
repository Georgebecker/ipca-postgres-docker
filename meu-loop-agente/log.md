# Log de Iterações — Loop Engineering

# Log de Iterações — Termômetro (Degrau 1)

## Template de ciclo
### Ciclo N — [data]
- **Hipótese:**
- **Mudança pequena:**
- **Teste:**
- **Medição:**
- **Decisão:** ACEITO / REJEITADO
- **Observações:**

---

## Iteração 1
- **Hipótese**: Converter a serie 433 do BCB em seed.sql com 563 linhas prontas para carga (561 reais + 2 ficticias de 2099)
- **Arquivos alterados**: docker-compose.yml, meu-loop-agente/workspace/db/init.sql, meu-loop-agente/workspace/db/seed.sql, meu-loop-agente/workspace/db/verificacao.sql, meu-loop-agente/workspace/scripts/baixar_dados.py, meu-loop-agente/workspace/scripts/gerar_seed.py, README.md
- **Métrica antes**: 0 linhas
- **Métrica depois**: 563 linhas
- **Melhoria**: 0.00%
- **Comandos passaram**: Sim
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T17:27:01Z

## Iteração 2
- **Hipótese**: Expor 3 endpoints FastAPI (health, ultimo, serie) lendo a tabela ipca
- **Arquivos alterados**: meu-loop-agente/workspace/api/ (requirements, Dockerfile, app/), docker-compose.yml, .env.example, README.md
- **Métrica antes**: 0 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: não calculável (a base era zero)
- **Comandos passaram**: Sim
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T17:44:00Z
- **Fonte da medição**: DECLARADA pelo dono (29/10/2026). O verificador não rodou na máquina que escreveu este log, porque ela não tem Docker; a contagem de 3 vem da verificação manual do dono, não de `medir_endpoints.py`.

## Iteração 3
- **Hipótese**: Fechar o Degrau 1 com os 3 endpoints respondendo e o banco populado
- **Arquivos alterados**: docs/adr/0001-por-que-postgresql.md, docs/proximo-degrau.md, README.md, baseline.json
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% (nenhuma mudança de métrica; o ciclo é de encerramento e documentação)
- **Comandos passaram**: Sim
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T17:44:00Z
- **Fonte da medição**: DECLARADA pelo dono (29/10/2026). Mesma ressalva da Iteração 2: sem Docker na máquina que escreveu o log, o número é o informado, não o medido pelo verificador.

## Iteração 4
- **Hipótese**: Um instalador interativo reduz os passos manuais e evita esquecer etapa (por exemplo, subir o banco sem carregar os dados)
- **Arquivos alterados**: instalar.py, docker-compose.mysql.yml, meu-loop-agente/workspace/db/mysql/init.sql, meu-loop-agente/workspace/scripts/gerar_seed.py, .env.example, README.md, docker-compose.yml (comentários linha a linha)
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% — iteração de ferramenta e documentação; a métrica do degrau não muda
- **Comandos passaram**: Sim (`py_compile`, menu do instalador, verificação de pré-requisitos, YAML dos dois compose, seed nos dois dialetos)
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T18:00:00Z
- **Fonte da medição**: parcialmente medida — `py_compile`, o menu, a geração do seed e a validação de YAML rodaram nesta máquina; nada que dependa de Docker foi executado
- **Justificativa do aceite**: a regra do loop ("sem melhora, sem mudança") vale para a métrica do degrau. Esta iteração não busca movê-la: entrega ferramenta de operação, aprovada pelo dono. Fica registrada para não sair do histórico.
