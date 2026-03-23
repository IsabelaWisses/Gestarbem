import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="gestarbem"
)

cursor = conn.cursor()

# Verificar tabela usuario
try:
    cursor.execute("DESCRIBE usuario")
    print("Estrutura da tabela 'usuario':")
    for col in cursor.fetchall():
        print(f"  {col[0]} - {col[1]}")
except:
    print("Tabela 'usuario' não existe")

# Verificar tabela users
print("\n")
try:
    cursor.execute("DESCRIBE users")
    print("Estrutura da tabela 'users':")
    for col in cursor.fetchall():
        print(f"  {col[0]} - {col[1]}")
except:
    print("Tabela 'users' não existe - PRECISA SER CRIADA!")

cursor.close()
conn.close()
