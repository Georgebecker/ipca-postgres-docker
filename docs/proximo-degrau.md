# Próximo degrau

O Degrau 1 terminou com banco, seed e API funcionando, mas sem nenhuma prova automática:
cada verificação foi manual, por `curl` e por consulta SQL no terminal.

O **Degrau 2 (Prova Real)** entra onde este parou: **testes automatizados** e **CI/CD**
(integração contínua, que roda os testes a cada push). Essas duas coisas ficaram fora de
propósito: testar sem ter o que testar seria decorar ferramenta, e pipeline sem teste só
automatiza o erro.

O banco, a modelagem e a API daqui seguem como estão — são a base que aqueles testes vão
exercitar.
