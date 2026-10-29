# Regras de Ouro — Análise de Dados (Python + SQL) e Loop Engineering

> Contrato de estudo e trabalho com dados. A Parte IV rege o agente de Loop Engineering (DeepSeek Flash).
>
> George Herman Becker · Gestão em Tecnologia da Informação
> Apoie: PIX `a8b68e14-edfe-4450-88f2-c2af4aca2a6c` · buymeacoffee.com/georgehbecker · linkedin.com/in/georgehbecker

---

# Regras de Ouro — ipca-postgres-docker

## Escopo do Degrau 1
- Modelagem de banco relacional (PostgreSQL).
- Docker e Docker Compose.
- Seed (dados reais do BCB + fictícios).
- API FastAPI com 3 endpoints.
- Verificação manual (sem testes automatizados).
- Registro de ciclos no log.

## Fora do escopo (não fazer neste degrau)
- Front-end.
- Testes automatizados.
- CI/CD.
- MongoDB, Redis.
- Deploy em servidor.

## Regra de atuação do agente
- Só atua dentro de `workspace/`.
- Uma mudança pequena por ciclo.
- Toda mudança precisa ser medida e registrada no log.

## Regra de documentação
- README, NOTES, log e ADR sempre atualizados.
- Toda decisão técnica registrada com o “porquê”.