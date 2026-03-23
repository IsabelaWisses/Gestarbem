import mysql.connector

print("Testando conexão com MySQL...")

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root"
    )
    print(" Conexão com MySQL OK!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    print("\nBancos de dados disponíveis:")
    for db in databases:
        print(f"  - {db[0]}")
    
    cursor.execute("SHOW DATABASES LIKE 'gestarbem'")
    if cursor.fetchone():
        print("\n Banco 'gestarbem' encontrado!")
        
        conn.database = "gestarbem"
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nTabelas no banco gestarbem:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("\n Banco 'gestarbem' NÃO encontrado!")
        print("Execute o script SQL: mysql -u root -p < gestarbem.sql")
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print(f" Erro: {e}")
    print("\nPossíveis soluções:")
    print("1. Verifique se o MySQL está rodando")
    print("2. Verifique usuário e senha (padrão: root/root)")
    print("3. Execute: mysql -u root -p < gestarbem.sql")
