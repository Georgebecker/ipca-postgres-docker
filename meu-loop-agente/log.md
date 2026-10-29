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

## Iteração 5
- **Hipótese**: Uma central de operação (menu) reduz o esforço diário de baixar dado, gerar seed, subir/derrubar, ver log, conferir dados e ver estado — sem decorar comando
- **Arquivos alterados**: meu-loop-agente/workspace/config.py (novo), docs/evidencias/09-menu-config.txt e 10-estado-sem-docker.txt (novos), docs/evidencias/LEIA-ME.md
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% — iteração de ferramenta; a métrica do degrau não muda
- **Comandos passaram**: Sim (`py_compile`; menu abriu e encerrou com código 0; opção 7 rodou sem Docker e degradou com aviso, sem quebrar)
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T18:10:00Z
- **Fonte da medição**: parcialmente medida — só o que não depende de Docker foi executado; subir, derrubar, logs, consultas e contagem de linhas ficaram sem prova nesta máquina
- **Justificativa do aceite**: mesma da Iteração 4 — ferramenta de operação, não melhoria de métrica. O `config.py` reaproveita as funções do `instalar.py` para não criar duas versões da mesma regra.

## Iteração 6
- **Hipótese**: O instalador anterior agia sem conferir pré-condição em várias ações (subir, aplicar SQL, desinstalar) e as falhas não diziam o que fazer; readaptar com condicionante → motivo → padrão em todo passo deve reduzir erro silencioso
- **Arquivos alterados**: instalar.py (readaptado), docs/evidencias/01, 02, 11 e 12, docs/evidencias/LEIA-ME.md
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% — iteração de robustez de ferramenta; a métrica do degrau não muda
- **Comandos passaram**: Sim (`py_compile`; menu encerrou com código 0; opção inválida explicada e repetida; opção 4 sem Docker parou na condicionante, com motivo e próximo passo)
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T18:20:00Z
- **Fonte da medição**: parcialmente medida — os três cenários de tela rodaram nesta máquina; os caminhos que tocam Docker (subir, aplicar SQL, desinstalar de verdade) seguem sem prova aqui
- **O que mudou na prática**: `exigir_docker`, `exigir_env` e `exigir_arquivo` passaram a rodar ANTES de cada comando; `perguntar_opcao` repete com explicação quando a resposta é inválida; `rodar` ganhou `dica_se_falhar`, que imprime o próximo passo concreto; e uma rede de segurança no `__main__` converte exceção não prevista em mensagem legível

## Iteração 7
- **Hipótese**: A opção 8 "não fazia nada" porque, ao falhar, `instalar_tudo` voltava ao menu sem anunciar a interrupção; e o `getpass` pedia a senha sem avisar antes, parecendo travado
- **Arquivos alterados**: instalar.py (`instalar_tudo` com etapas numeradas e mensagem de interrupção; `criar_env` com aviso prévio da senha e guarda de terminal não interativo), docs/evidencias e docs/img (nova evidência 13)
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% — correção de comunicação; a métrica do degrau não muda
- **Comandos passaram**: Sim (`py_compile`; opção 8 anunciou etapas 1/6 e interrompeu com causa, lista do que deu certo e próximo passo; opção 2 em cópia isolada mostrou o aviso da senha e tratou stdin não interativo sem travar)
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T18:30:00Z
- **Fonte da medição**: parcialmente medida — os dois cenários rodaram nesta máquina; o caminho com Docker (etapas 4 a 6) segue sem prova aqui
- **Cuidado tomado**: o teste de `criar_env` rodou numa cópia em diretório temporário, para não sobrescrever o `.env` real do dono (conferido depois: 26 linhas, 694 bytes, inalterado)

## Iteração 8
- **Hipótese**: Adaptar API e scripts para o banco na nuvem (Neon) sem perder o modo Docker
- **Arquivos alterados**: instalar.py, meu-loop-agente/workspace/api/app/{config,database,routes}.py, meu-loop-agente/workspace/scripts/aplicar_sql_nuvem.py, README.md, .env.example
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0.00%
- **Comandos passaram**: Sim
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T19:49:32Z
- **Fonte da medição**: MEDIDA — a API subiu localmente apontando para o Neon e os 3 endpoints responderam 200 (`endpoints ok: 3`), não é declaração
- **Justificativa do aceite**: o verificador sugeriu REJEITADO porque a métrica não mudou (3 → 3); a decisão do dono foi ACEITO porque o objetivo é adaptar o ambiente, não melhorar a métrica — e pela primeira vez a medição foi real, não declarada

## Iteração 9
- **Hipótese**: A verificação dizia apenas "ok"/"falhou" por endpoint. Mostrar, para cada um, o comando reproduzível, o resultado esperado, o resultado obtido e o motivo do veredito transforma o teste em prova que o dono pode repetir sozinho — e permite comparar o número (563 registros, 561 reais) em vez de confiar no "verde"
- **Arquivos alterados**: instalar.py (`testar_endpoints` reescrito com `CASOS_DE_TESTE` e `_resumir_corpo`; nova `mostrar_comandos_manuais` na opção 10), docs/evidencias/17-testes-com-feedback.txt (novo), docs/img/18-testes-com-feedback.png (novo), docs/img/LOG-IMAGENS.md
- **Métrica antes**: 3 endpoints
- **Métrica depois**: 3 endpoints
- **Melhoria**: 0,00% — iteração de prova e comunicação; a métrica do degrau não muda
- **Comandos passaram**: Sim (`py_compile`; opção 7 executou 4 casos e reportou "4 de 4 testes passaram"; opção 10 listou todos os comandos manuais por ambiente)
- **Decisão**: ACEITO
- **Data/hora**: 2026-10-29T20:05:00Z
- **Fonte da medição**: MEDIDA — os 4 casos rodaram contra a API no ar apontando para o Neon e os números vieram do banco (`/ipca/serie` = 563 itens, `?tipo=real` = 561 itens)
- **Justificativa do aceite**: o ganho não está na métrica, e sim na dirigibilidade: qualquer pessoa repete o comando do curl, compara com o esperado escrito na tela e entende por que passou ou falhou. É o mesmo princípio do degrau — evidência, não opinião

