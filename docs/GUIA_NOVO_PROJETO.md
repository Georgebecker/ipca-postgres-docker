# Guia — criar um novo projeto a partir desta base

> Esta base (`ipca-postgres-docker`) é o **modelo padrão** dos novos projetos.
> Regra: todo projeto novo nasce daqui, igual — só muda o nome.

## Caminho rápido (1 comando)

```powershell
cd d:\Projetos\ipca-postgres-docker
powershell -ExecutionPolicy Bypass -File scripts\criar_projeto_base.ps1 -Nome projeto_x -Venv
```

O script:
1. copia a base para `D:\Projetos\<nome>`;
2. troca `ipca-postgres-docker` / `IPCA Postgres Docker` pelo nome novo nos textos;
3. inicia o git, ativa os ganchos que bloqueiam o `.env` (no commit e no envio) e faz o commit inicial;
4. com `-Venv`, cria o ambiente virtual (`.venv`).

Parâmetros: `-Nome` (obrigatório) · `-Titulo "Nome Bonito"` (opcional) · `-Destino` (padrão `D:\Projetos`) · `-Venv` (opcional).

## Lista de arquivos base (o que sempre vai)

| Item | Vai para o git? |
|------|-----------------|
| `README.md` | sim |
| `LICENSE` | sim |
| `.gitignore` | sim |
| `.env.example` | sim |
| `.githooks/` (`pre-commit`, `pre-push`, `instalar.ps1`, `README.md`) | sim |
| `docs/REGRAS_DE_OURO.md` | sim |
| `docs/GUIA_NOVO_PROJETO.md` | sim |
| `.gitattributes` | sim |
| `requirements.txt` | sim |
| `meu-loop-agente/` (contrato do loop, verificador, baseline, log) | sim |
| `.github/agents/` (agente padrão do Copilot) | sim |
| `data/raw/`, `data/processed/`, `data/descartados/`, `notebooks/` (só `.gitkeep`) | sim |
| `.env` | **NÃO** — bloqueado por `.gitignore` + ganchos (`pre-commit` e `pre-push`) |
| `.venv/`, dados, logs, `saidas/`, caches | **NÃO** |

## Passo a passo manual (só se precisar)

1. Copiar: `README.md`, `LICENSE`, `.gitignore`, `.gitattributes`, `requirements.txt`, `.env`, `.env.example`, `.githooks/`, `.github/`, `meu-loop-agente/`, `docs/REGRAS_DE_OURO.md`, `docs/GUIA_NOVO_PROJETO.md` e as pastas `data/...` e `notebooks/` (com `.gitkeep`).
2. Ajustar `PROJETO_NOME=...` no `.env` e no `.env.example`; ajustar o título no `README.md`.
3. `git init` → `git config core.hooksPath .githooks` → `git add .` (conferir: `.env` fora) → commit inicial.

## Conferência final (30 segundos)

```powershell
git log --oneline -1
git ls-files | findstr /i ".env"   # só pode aparecer .env.example
git config core.hooksPath          # esperado: .githooks
```

Os ganchos do `.githooks` (`pre-commit` e `pre-push`) são a barreira que garante
que o `.env` NUNCA vai para o git — nem no commit, nem no envio ao repositório.
