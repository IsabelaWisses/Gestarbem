import mysql.connector
import sys

configs = [
    {"host": "localhost", "user": "root", "password": ""},
    {"host": "localhost", "user": "root", "password": "root"},
    {"host": "localhost", "user": "root", "password": "mysql"},
    {"host": "127.0.0.1", "user": "root", "password": ""},
    {"host": "127.0.0.1", "user": "root", "password": "root"},
]

print("Testando conexoes MySQL...\n")

for i, cfg in enumerate(configs, 1):
    try:
        conn = mysql.connector.connect(**cfg)
        print(f"OK Config {i} FUNCIONOU!")
        print(f"   host={cfg['host']}, user={cfg['user']}, password='{cfg['password']}'")
        
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        dbs = [db[0] for db in cursor.fetchall()]
        
        if 'gestarbem' in dbs:
            print(f"   OK Database 'gestarbem' existe!")
        else:
            print(f"   AVISO Database 'gestarbem' NAO existe. Criando...")
            cursor.execute("CREATE DATABASE gestarbem")
            print(f"   OK Database 'gestarbem' criado!")
        
        cursor.close()
        conn.close()
        
        print(f"\nAtualize database.py com estas credenciais:")
        print(f"   password=\"{cfg['password']}\"")
        sys.exit(0)
        
    except mysql.connector.Error as e:
        print(f"ERRO Config {i} falhou: {e}")

print("\nTeste concluido!")
