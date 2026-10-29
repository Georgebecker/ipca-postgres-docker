# Log das imagens

Cada imagem abaixo foi gerada a partir da **saida real** do programa, capturada
pelo terminal no dia 29/10/2026. O texto dentro da imagem e exatamente o que o
programa imprimiu — nada foi digitado a mao.

**Ressalva de honestidade:** a imagem e **desenhada** a partir do texto real
(fonte monoespaçada, fundo escuro), **nao e um screenshot** da janela do
terminal. O conteudo e fiel; o enquadramento e feito por codigo. Um print real
da tela pode ser tirado a qualquer momento com os comandos da coluna
**Como reproduzir**.

| Imagem | O que prova | Como reproduzir | Texto puro |
|---|---|---|---|
| `01-menu-instalador.png` | menu do instalador | `python instalar.py` com entrada `0` | `docs/evidencias/01-menu-instalador.txt` |
| `02-pre-requisitos.png` | verificacao de pre-requisitos | `python instalar.py` com entrada `1, 0` | `docs/evidencias/02-pre-requisitos.txt` |
| `11-opcao-invalida.png` | resposta invalida no menu | `python instalar.py` com entrada `x, 0` | `docs/evidencias/11-opcao-invalida.txt` |
| `12-sem-docker-condicionante.png` | condicionante do Docker (opcao 4) | `python instalar.py` com entrada `4, 0` | `docs/evidencias/12-sem-docker-condicionante.txt` |

## Por que nao ha print da tela

A maquina que executa os testes nao tem uma janela de terminal visivel para
mim no momento da captura: os comandos rodam em segundo plano e a saida volta
como texto. Por isso a imagem e gerada do texto, e nao fotografada da tela.
Se quiser o print real, rode o comando da coluna **Como reproduzir** com o
terminal aberto e tire a captura — a legenda ja esta escrita acima.
