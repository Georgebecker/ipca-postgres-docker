# Regras de Ouro — Análise de Dados (Python + SQL) e Loop Engineering

> Contrato de estudo e trabalho com dados. A Parte IV rege o agente de Loop Engineering (DeepSeek Flash).
>
> George Herman Becker · Gestão em Tecnologia da Informação
> Apoie: PIX `a8b68e14-edfe-4450-88f2-c2af4aca2a6c` · buymeacoffee.com/georgehbecker · linkedin.com/in/georgehbecker

---

## Parte I — Postura (como pensar)

**R1. Comece pelas perguntas, não pelos dados.**
Toda análise existe para responder algo. Escreva a pergunta antes de abrir a base. Sem pergunta, não há análise — há só um passeio pelos dados.

**R2. Seja cético e defensor ao mesmo tempo.**
Defenda o insight que encontrou, mas tente derrubá-lo: "que dado mostraria que isto está errado?". A desconfiança metódica separa o achismo da conclusão.

**R3. Correlação não é causalidade.**
Duas coisas se moverem juntas não prova que uma causa a outra. Procure fatores escondidos e diga, com clareza, o que os dados permitem ou não afirmar.

**R4. Aceite a ignorância e o erro.**
"Eu não sei" é resposta profissional. Reconhecer o erro cedo constrói credibilidade; escondê-lo gera retrabalho e desconfiança.

**R5. A palavra tem valor.**
Só afirme o que foi verificado. Nada de "deve estar certo" sem olhar o dado; nada de entregar conclusão sem testar o caminho.

## Parte II — Processo (como trabalhar)

**R6. Siga o ciclo rigoroso antes de concluir:**
perguntar → coletar → **validar** (o dado é o que parece?) → **descrever** (o que ele diz, com neutralidade?) → **avaliar** (isso é bom ou ruim, e para quem?). Separar essas etapas evita enxergar só o que se espera ver.

**R7. Valide antes de confiar.**
Encoding, formato, tipos, nulos, duplicatas, amostra visual. Dado não validado não entra em análise nem em `data/processed/`.

**R8. Meça duas vezes.**
Calcule a mesma métrica por caminhos diferentes (ou fontes diferentes). Se os números discordam, há bug ou suposição errada — melhor descobrir agora.

**R9. Exija reprodutibilidade.**
Mesmo dado + mesmo código = mesmo número. Fixe sementes aleatórias, versione código e parâmetros, registre o passo a passo. Resultado que só acontece na sua sessão não é resultado.

**R10. Padrão primeiro, específico depois.**
Antes de confiar em métrica nova ou recorte especial, confira as medidas básicas (totais, contagens, médias). Elas já foram validadas milhares de vezes.

**R11. Hipótese sem evidência é palpite.**
Ao notar anomalia ou tendência, escreva a teoria e procure dados que a confirmem OU a derrubem. Contar a história e tentar prová-la errada é o teste final.

**R12. Compare com o que já se sabe.**
Um número muito diferente do histórico ou de outra fonte não é insight fabuloso: é suspeito até prova em contrário.

**R13. Anote tudo que aprender.**
Princípios, regras, nomes, estados, decisões — registrados na hora. O problema de trabalho longo com dados não é processar; é esquecer.

## Parte III — Técnica (Python, SQL e os dados)

**R14. Olhe a distribuição, não só a média.**
Média engana. Histogramas, contagens por categoria e quartis revelam o que os resumos escondem (multimodalidade, caudas, concentrações).

**R15. Outliers são canários de mina.**
Antes de descartar um ponto estranho, entenda por que ele existe: pode ser dado corrompido, filtro errado ou um fenômeno real e importante.

**R16. O ruído existe e engana.**
Pequenas diferenças podem ser só aleatoriedade. Pergunte sempre: "mesmo que seja verdade, isso importa na prática?".

**R17. Confira exemplos reais.**
Todo código novo de análise exige olhar linhas de verdade: amostras de cada grupo, valores extremos, o que parecer estranho. Resumo sem olhar o detalhe é fé, não verificação.

**R18. Divida os dados e compare subgrupos.**
A métrica geral pode esconder comportamentos opostos entre grupos (Paradoxo de Simpson). Compare também períodos de tempo — dias e meses revelam falhas silenciosas de coleta.

**R19. Conte e declare cada filtro.**
Quase toda análise filtra dados. Registre quantas linhas saem em cada etapa e por quê. Filtro invisível é conclusão enganosa.

**R20. Proporção precisa de numerador e denominador claros.**
"Taxa de X" só faz sentido se todos souberem o que conta em cima e embaixo. Defina os dois e mantenha a mesma definição em toda comparação.

**R21. Escreva código pequeno, legível e testado.**
Funções curtas com um propósito, nomes que dizem o que fazem e uma checagem real antes de declarar pronto. Quando o dado mudar, o teste avisa — o achismo não.

**R22. SQL: entenda o dado antes de juntar.**
Antes do `JOIN`, conheça chaves, cardinalidade e nulos das duas tabelas. Junção errada soma ou multiplica linhas em silêncio. Comece simples, confira contagens, evolua.

**R23. Notebook é rascunho; script é produto.**
Notebooks servem para explorar e aprender. O que virar rotina ou entrega vira `.py` organizado, com entrada e saída claras, pronto para rodar de novo.

---

## Parte IV — Loop Engineering (o jeito de trabalhar do agente)

> Agente (DeepSeek Flash) que melhora sistemas em ciclos contínuos e verificáveis:
> ler contrato → propor UMA hipótese pequena → aplicar → verificar → medir → decidir
> (ACEITO mantém e atualiza a linha de base; REJEITADO reverte na hora) → registrar no log → repetir até a meta.
>
> Prompt de operação: `meu-loop-agente/system_prompt.md`. Contrato: `meu-loop-agente/program.md`.

**R24. Contrato antes do ciclo.**
Objetivo, métrica principal, arquivos permitidos/proibidos, comandos de verificação e critérios de aceite/rejeição ficam escritos em `program.md` antes de qualquer mudança. O humano escreve e revisa; o agente lê e segue. Sem contrato, não há ciclo.

**R25. Uma hipótese pequena por iteração.**
Cada ciclo propõe UMA melhoria localizada, com diff pequeno (menos de 50 linhas). Mudança grande mistura efeitos, esconde a causa e encarece a reversão.

**R26. Medir, nunca estimar.**
A métrica é lida do resultado real (o verificador roda o comando e captura o número) e comparada com o melhor valor registrado. "Parece que melhorou" não vale como resultado.

**R27. Sem melhora, sem mudança.**
Comando falhou ou métrica não melhorou? Reverte na hora e registra como REJEITADO. O sistema só acumula o que melhora de verdade.

**R28. Toda iteração entra no log.**
Hipótese, arquivos alterados, métrica antes/depois, decisão e data vão para o `log.md`. É o log que permite continuar de onde parou — na mesma sessão ou meses depois.

**R29. Escopo fechado.**
O agente só modifica arquivos permitidos dentro de `workspace/`. `.env`, segredos, deploy e workflows são proibidos.

**R30. Ponto de retorno antes de cada ciclo.**
Commit antes de mexer (ou, no mínimo, o estado anterior registrado). Reverter precisa ser um comando, nunca uma arqueologia.

**R31. Saber parar.**
Critérios explícitos: meta atingida, número máximo de iterações, rejeições seguidas demais ou falta de hipóteses plausíveis. Ciclo que não para queima tempo, recursos e confiança.

**R32. Consistência acima de criatividade.**
Para o DeepSeek Flash: temperatura baixa (0.2–0.3), instruções específicas (listas e comandos exatos — o modelo pode ignorar instruções vagas) e contrato curto. Uma hipótese por ciclo, sempre no mesmo formato: previsível, repetível, auditável.

**R33. Idioma de trabalho: português do Brasil.**
Tudo que o agente escreve — resposta no chat, entrada no log, mensagem de commit, comentário no código, aviso de erro — sai em **português do Brasil**. Nunca responder em outro idioma: nem uma frase, nem um título, nem um caractere solto por engano. Nome técnico consagrado (commit, log, deploy, pipeline, branch) pode ficar como está; a frase em volta é em português. Única exceção: quando o próprio usuário pedir outro idioma. Fora disso, o padrão é sempre pt-BR.

**R34. `.env` em todo projeto, sem exceção.**
Todo projeto tem `.env` (local, nunca versionado) e `.env.example` (modelo, versionado). Template e cópia: `novo-env.ps1` (nunca sobrescreve `.env` existente; garante a proteção no `.gitignore` antes de criar o arquivo). Segredo sem proteção está a um `git add -A` de vazar.

**R35. Saber qual modelo está respondendo.**
Antes de culpar a sessão por lentidão, identifique o modelo (`modelo-ativo.ps1`). Modelo atual: **deepseek-v4-flash**. Em tarefa grande, avise o usuário e prefira passos poucos e direcionados — economia de contexto é o que mais acelera.

**R36. Chave de API só na máquina local, nunca em arquivo versionado.**
Nenhum valor de chave — DeepSeek, OpenAI, Google, Hugging Face, token, senha, DSN ou chave privada — em `.env.example`, README, código, issue, print ou log. `.env` é local e pode guardar o valor; o preferível é a variável de ambiente do usuário do Windows (escopo `User`). O código lê com `os.getenv`. Nunca imprimir o valor em resposta, log ou commit; nunca commitar `.env`; nunca usar `git add -f` em arquivo de segredo. Ferramentas: `segredos.ps1 -Listar` (só nomes), `-Definir NOME` (grava sem exibir), `-ConferirArquivos` (audita), `-MigrarArquivos` (move para o ambiente sem descartar valor em conflito).

---

## Qualidade de dados — o checklist antes de usar qualquer base

- **Acurácia:** o valor representa a realidade? (confira amostras)
- **Completude:** há nulos onde não deveria haver?
- **Consistência:** o mesmo conceito está escrito do mesmo jeito na base inteira?
- **Unicidade:** há duplicatas que não deveriam existir?
- **Validade:** os valores respeitam o formato esperado (data, moeda, domínio, encoding)?
- **Atualidade:** o dado corresponde ao período que interessa à análise?

**Fluxo imutável do pipeline:** bruto → tratado/validado → usado.
- `data/raw/` guarda o dado como veio do mundo; não se altera (é a prova original).
- `data/processed/` só recebe o que passou no checklist e ficou documentado.
- Nada se apaga: o que não servir vai para descarte, decidido com calma.

## Arquitetura e organização do projeto

- Pastas e nomes padronizados desde o primeiro dia; uma convenção única para todo o projeto.
- Fonte única de verdade para regras e limites (arquivo de configuração + `.env`).
- Segredos e caminhos locais só no `.env`; o `.env.example` (modelo, sem segredos) é o único arquivo `.env*` versionado.
- Proteção de segredos em camadas: `.gitignore` ignora `.env` e variações; conferir `git status` antes de todo `git add`; `git rm --cached .env` se aparecer; nunca `git add -f` em segredo; ganchos de pré-commit e pré-push ativos (`.githooks/`) recusam commit e envio; auditoria com `segredos.ps1`. Chave exposta é chave queimada: na dúvida, revogar na origem.
- Regras globais do usuário (pt-BR, `.env` em todo projeto, modelo ativo) ficam em `%USERPROFILE%\.copilot\instructions\` e valem em qualquer workspace. R33–R36 apontam para elas.
- Git: commits pequenos e descritivos, **somente após teste real com resultado positivo**. Nunca versionar `.env`, dados brutos grandes ou caches.
- Backup antes de operação destrutiva (conversão, sobrescrita, reorganização), com data no nome e política de retenção. Testar a restauração: backup que não volta não é backup.
- Recursos da máquina são finitos: uma tarefa pesada por vez, memória conferida antes de scans grandes.

## Progresso e comunicação

- Tarefa longa mostra **progresso real** (percentual), nunca um "rodando" sem número.
- Comunicação com leigos em linguagem clara: o que aconteceu, o que falta, um passo para agir; detalhes técnicos ficam escondidos ("ver detalhes").
- Toda entrega de análise conta uma história apoiada nos números, com a visualização certa para cada mensagem.

## Conviver com IA sem perder o rigor

- Pedir código funcional com explicação curta; se a IA não souber, que diga "não sei" em vez de inventar.
- Dividir tarefas grandes em etapas pequenas e verificáveis — e conferir cada etapa.
- Nunca aceitar código ou conclusão sem rodar e ver o resultado com os próprios olhos.
- Lições boas de conversa viram regra, documento ou módulo — não ficam presas no chat.

---

## Resumo em uma frase

> Pergunte primeiro, valide antes de confiar, meça duas vezes, olhe os dados com os próprios olhos, desconfie do que parece bom demais, escreva código simples e testado, anote tudo que aprender — e só entregue o que de fato verificou.