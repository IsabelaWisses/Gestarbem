import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gestarbem"
)

cursor = conn.cursor()

# Criar tabela users
create_table_query = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    semana_gestacional INT,
    foto VARCHAR(255),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

try:
    cursor.execute(create_table_query)
    conn.commit()
    print("[OK] Tabela 'users' criada com sucesso!")
    
    # Verificar estrutura
    cursor.execute("DESCRIBE users")
    print("\nEstrutura da tabela 'users':")
    for col in cursor.fetchall():
        print(f"  {col[0]} - {col[1]}")
        
except Exception as e:
    print(f"[ERRO] Erro ao criar tabela: {e}")

cursor.close()
conn.close()
