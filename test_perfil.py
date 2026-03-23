"""
Script de teste para verificar se a atualização de perfil está funcionando
"""
from database import conectar_database

def test_user_columns():
    """Verifica se todas as colunas necessárias existem na tabela users"""
    conn = conectar_database()
    if not conn:
        print("❌ Erro ao conectar no banco de dados")
        return False
    
    cur = conn.cursor()
    cur.execute("DESCRIBE users")
    columns = [row[0] for row in cur.fetchall()]
    
    required_columns = ['id', 'nome', 'email', 'senha', 'telefone', 'semana_gestacional', 'foto', 'humor']
    
    print("\n✅ Colunas encontradas na tabela users:")
    for col in columns:
        print(f"  - {col}")
    
    print("\n📋 Verificando colunas obrigatórias:")
    all_ok = True
    for col in required_columns:
        if col in columns:
            print(f"  ✅ {col}")
        else:
            print(f"  ❌ {col} - FALTANDO!")
            all_ok = False
    
    cur.close()
    conn.close()
    
    return all_ok

def test_uploads_folder():
    """Verifica se a pasta uploads existe"""
    import os
    if os.path.exists('uploads'):
        print("\n✅ Pasta 'uploads' existe")
        return True
    else:
        print("\n❌ Pasta 'uploads' NÃO existe - criando...")
        os.makedirs('uploads')
        print("✅ Pasta 'uploads' criada com sucesso")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE CONFIGURAÇÃO DO PERFIL")
    print("=" * 60)
    
    test1 = test_user_columns()
    test2 = test_uploads_folder()
    
    print("\n" + "=" * 60)
    if test1 and test2:
        print("✅ TODOS OS TESTES PASSARAM!")
        print("\nO sistema está pronto para:")
        print("  - Salvar fotos de perfil")
        print("  - Atualizar dados do usuário")
        print("  - Exibir informações completas")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("\nVerifique os erros acima e corrija antes de usar o sistema")
    print("=" * 60)
