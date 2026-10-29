# Log das imagens

Cada imagem foi gerada a partir da **saída real** do programa, capturada pelo
terminal em 29/10/2026. O texto dentro da imagem é exatamente o que o programa
imprimiu — nada foi digitado à mão.

**Ressalva de honestidade:** a imagem é **desenhada** a partir do texto real
(fonte monoespaçada, fundo escuro), **não é um screenshot** da janela do terminal.
O conteúdo é fiel; o enquadramento é feito por código. Um print real pode ser tirado
a qualquer momento com o comando da coluna **Como reproduzir**.

| Imagem | O que prova | Como reproduzir | Texto puro |
|---|---|---|---|
| `01-menu-instalador.png` | menu do instalador | `python instalar.py` com entrada `0` | `docs/evidencias/01-menu-instalador.txt` |
| `02-pre-requisitos.png` | verificacao de pre-requisitos | `python instalar.py` com entrada `1, 0` | `docs/evidencias/02-pre-requisitos.txt` |
| `11-opcao-invalida.png` | resposta invalida no menu | `python instalar.py` com entrada `x, 0` | `docs/evidencias/11-opcao-invalida.txt` |
| `12-sem-docker-condicionante.png` | condicionante do Docker (opcao 4) | `python instalar.py` com entrada `4, 0` | `docs/evidencias/12-sem-docker-condicionante.txt` |
| `13-opcao-8-etapas.png` | opcao 8 (instalar tudo) anuncia as etapas | `python instalar.py` com entrada `8, 0` | `docs/evidencias/13-opcao-8-etapas.txt` |

## Por que não há print da tela

Os comandos rodam em segundo plano e a saída volta como texto: não há janela de
terminal visível para fotografar no momento da captura. Por isso a imagem é gerada
do texto. Para o print real, rode o comando da coluna **Como reproduzir** com o
terminal aberto — a legenda já está escrita acima.
