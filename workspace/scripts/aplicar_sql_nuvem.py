import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Carrega as variaveis do .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL nao encontrada no .env. Verifique o arquivo .env na raiz.")

# Descobre a raiz do projeto (a pasta onde o .env esta)
BASE_DIR = Path(__file__).resolve().parent
while not (BASE_DIR / ".env").exists() and BASE_DIR != BASE_DIR.parent:
    BASE_DIR = BASE_DIR.parent

# O agente pode ter salvado em dois lugares diferentes. Vamos testar os dois.
INIT_SQL_1 = BASE_DIR / "meu-loop-agente" / "workspace" / "db" / "init.sql"
INIT_SQL_2 = BASE_DIR / "workspace" / "db" / "init.sql"
SEED_SQL_1 = BASE_DIR / "meu-loop-agente" / "workspace" / "db" / "seed.sql"
SEED_SQL_2 = BASE_DIR / "workspace" / "db" / "seed.sql"

# Escolhe o caminho que realmente existe
INIT_SQL = INIT_SQL_1 if INIT_SQL_1.exists() else INIT_SQL_2
SEED_SQL = SEED_SQL_1 if SEED_SQL_1.exists() else SEED_SQL_2

if not INIT_SQL.exists():
    print(f"[ERRO FATAL] Nao achei o init.sql. Procurei em: \n- {INIT_SQL_1}\n- {INIT_SQL_2}")
    print("Por favor, procure onde o init.sql esta e me avise.")
    exit(1)
    
if not SEED_SQL.exists():
    print(f"[ERRO FATAL] Nao achei o seed.sql. Procurei em: \n- {SEED_SQL_1}\n- {SEED_SQL_2}")
    print("Por favor, procure onde o seed.sql esta e me avise.")
    exit(1)

def executar_arquivo_sql(caminho_arquivo, conexao):
    print(f"Lendo o arquivo {caminho_arquivo.name}...")
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        sql = f.read()
    
    with conexao.cursor() as cursor:
        # O psycopg2 as vezes precisa que o SQL seja executado em blocos se tiver muitos INSERTs
        try:
            cursor.execute(sql)
            conexao.commit()
        except Exception as e:
            conexao.rollback()
            raise e
            
    print(f"[OK] {caminho_arquivo.name} executado com sucesso no Neon!")

def main():
    print("Conectando ao banco no Neon...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        # 1. Cria a tabela
        executar_arquivo_sql(INIT_SQL, conn)
        
        # 2. Insere os dados
        executar_arquivo_sql(SEED_SQL, conn)
        
        # 3. Verifica a contagem
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM ipca;")
            total = cursor.fetchone()[0]
            print(f"\n[SUCESSO] Total de registros na tabela ipca: {total}")
            
        conn.close()
    except Exception as e:
        print(f"\n[ERRO] Falha ao executar: {e}")

if __name__ == "__main__":
    main()