import mysql.connector

def conectar_database():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="gestarbem"
        )
        return conexao
    except mysql.connector.Error as e:
        print(f"Erro ao conectar no MySQL: {e}")
        return None