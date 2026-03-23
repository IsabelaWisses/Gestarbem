import sys
import os

print("=== VERIFICACAO COMPLETA DO SISTEMA ===\n")

# 1. Verificar imports
print("1. Verificando imports...")
try:
    import flask
    print(f"   [OK] Flask {flask.__version__}")
except ImportError as e:
    print(f"   [ERRO] Flask: {e}")
    sys.exit(1)

try:
    import mysql.connector
    print(f"   [OK] MySQL Connector instalado")
except ImportError as e:
    print(f"   [ERRO] MySQL Connector: {e}")
    sys.exit(1)

try:
    from werkzeug.security import generate_password_hash, check_password_hash
    print(f"   [OK] Werkzeug instalado")
except ImportError as e:
    print(f"   [ERRO] Werkzeug: {e}")
    sys.exit(1)

# 2. Verificar conexão com banco
print("\n2. Verificando conexao com banco de dados...")
try:
    from database import conectar_database
    conn = conectar_database()
    if conn:
        print("   [OK] Conexao com MySQL estabelecida")
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        print(f"   [OK] Tabela 'users' acessivel ({count} registros)")
        
        cursor.close()
        conn.close()
    else:
        print("   [ERRO] Nao foi possivel conectar ao banco")
        sys.exit(1)
except Exception as e:
    print(f"   [ERRO] {e}")
    sys.exit(1)

# 3. Verificar templates
print("\n3. Verificando templates...")
templates = ["index.html", "home.html", "agenda.html", "documentalizar.html", 
             "lista.html", "perfil.html", "cadastro.html", "login.html"]
for template in templates:
    path = os.path.join("templates", template)
    if os.path.exists(path):
        print(f"   [OK] {template}")
    else:
        print(f"   [ERRO] {template} nao encontrado")

# 4. Verificar app.py
print("\n4. Verificando app.py...")
try:
    from app import app
    print("   [OK] Aplicacao Flask carregada")
    print(f"   [OK] Rotas registradas: {len(app.url_map._rules)}")
except Exception as e:
    print(f"   [ERRO] {e}")
    sys.exit(1)

print("\n=== SISTEMA PRONTO PARA USO ===")
print("\nPara iniciar o servidor:")
print("  py app.py")
print("\nAcesse: http://127.0.0.1:5000")
