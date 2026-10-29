# Imagem da API: Python enxuto (slim) + as dependencias do requirements.
# Nao copia o .env: credencial nunca entra na imagem.
FROM python:3.12-slim

# Evita que o Python grave .pyc e que o stdout fique em buffer (log aparece na hora).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copia so o requirements primeiro: enquanto ele nao mudar, o Docker reaproveita
# a camada de instalacao e o build fica rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Depois copia o codigo.
COPY app ./app

EXPOSE 8000

# 0.0.0.0 e obrigatorio dentro do container: 127.0.0.1 so aceitaria conexao
# de dentro do proprio container, e o navegador do host nunca chegaria.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
