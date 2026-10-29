# Ganchos de proteção do git — segurança máxima

Três ganchos em `sh` que impedem segredo de entrar no repositório e impedem que
um modelo de IA apareça como autor:

- `pre-commit` — roda **no commit**. Recusa o commit quando algum arquivo de segredo
  (`.env` ou variante) entra na lista, ou quando uma linha adicionada contém valor com
  cara de chave. Funciona inclusive com `git add -f`.
- `commit-msg` — roda **na mensagem**. Recusa o commit quando a mensagem traz
  `Co-authored-by:` apontando para Copilot, Claude, GPT, Gemini, DeepSeek, Cursor ou
  conta bot, além de rodapés `Assisted-by:` e `Generated with <modelo>`.
- `pre-push` — roda **no envio ao remoto**. É a segunda barreira: reanalisa os commits
  da fila (segredo, chave **e** coautoria de IA) e recusa o `push` mesmo que o commit
  tenha passado com `--no-verify`.

O único arquivo `.env*` permitido é o `.env.example` (modelo, sem valores).

## O que é considerado segredo

| Padrão | Origem |
|---|---|
| `sk-` seguido de 24 ou mais caracteres alfanuméricos | DeepSeek / OpenAI |
| `sk-proj-` | OpenAI (projeto) |
| `AIza` + 33 caracteres | Google (API key) |
| `hf_` + 30 caracteres | Hugging Face |
| `ghp_`, `github_pat_` | GitHub |
| `AKIA` + 16 caracteres maiúsculos | AWS |
| `-----BEGIN ... PRIVATE KEY-----` | chave privada |
| `NOME_DE_CHAVE` + `=`/`:` + valor de 16+ caracteres | atribuição em qualquer arquivo |

O valor da chave não mora em arquivo: mora na **variável de ambiente do usuário** do
Windows. Use `segredos.ps1 -Definir NOME_DA_CHAVE`.

## Autoria sempre humana

O `commit-msg` recusa a mensagem que credita um modelo de IA como coautor. O motivo é
prático: o GitHub monta a lista de contribuidores a partir de autoria e coautoria, e um
trailer `Co-authored-by:` apontando para Copilot, Claude ou GPT transforma a ferramenta
em contribuidora do projeto. Aqui a lista é de **pessoas**.

Teste rápido (a mensagem com trailer precisa ser recusada):

```powershell
$msg = "teste`n`nCo-authored-by: Copilot <copilot@github.com>"
$msg | Out-File "$env:TEMP\msg.txt" -Encoding utf8
& "C:\Program Files\Git\bin\bash.exe" -c "./.githooks/commit-msg '$env:TEMP\msg.txt'"
```

Para o trailer não ser gerado na origem, mantenha no VS Code `git.addAICoAuthor` em
`"off"`.

## Instalação

```powershell
# neste projeto (o script roda a partir de .githooks/)
powershell -ExecutionPolicy Bypass -File .githooks\instalar.ps1

# em todos os repositórios de uma raiz
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\.copilot\scripts\instalar-hooks.ps1" -Destino "D:\Projetos" -Todos
```

O instalador copia estes arquivos para `.githooks/` do projeto, garante fim de linha
LF (obrigatório para `sh`), registra `.githooks/* text eol=lf` no `.gitattributes` e
aponta `core.hooksPath` para `.githooks`.

## Teste rápido

Monte o valor falso em tempo de execução — assim este próprio arquivo não guarda um
texto com formato de chave (ele passa pelo mesmo gancho):

```powershell
$falso = 'sk-' + ('a' * 32)
"CHAVE_DE_TESTE=$falso" | Out-File .env -Encoding utf8
git add -f .env ; git commit -m "teste"     # o gancho recusa
git reset ; Remove-Item .env
```

## Por que três barreiras

Um commit pode ser criado com `--no-verify` (pulando o `pre-commit` e o `commit-msg`).
O `pre-push` examina os commits que estão sendo enviados e recusa o envio — então nem o
segredo nem a coautoria de IA chegam ao GitHub. Depois de remover um segredo, ainda é
preciso **revogar a chave na origem**: histórico reescrito não desfaz um vazamento.

## Falso positivo

A mensagem indica apenas o **arquivo** suspeito, nunca o valor. Se for um exemplo em
documentação ou um dado de teste, ajuste a linha para não parecer chave real (evite
sequências longas com prefixo de chave). Não existe marcador de exceção de propósito:
um atalho desses acabaria virando a porta de entrada do vazamento.
