print("🔧 Teste básico Python...")

try:
    # Teste 1: Python básico
    print("✅ Python funcionando")
    
    # Teste 2: Verificar arquivo .env
    import os
    if os.path.exists('.env'):
        print("✅ Arquivo .env encontrado")
        with open('.env', 'r') as f:
            lines = f.readlines()[:3]
            for line in lines:
                if 'DB_HOST' in line:
                    print(f"✅ {line.strip()}")
    else:
        print("❌ Arquivo .env não encontrado")
    
    # Teste 3: Verificar arquivo settings.py
    if os.path.exists('siteDjango/settings.py'):
        print("✅ arquivo settings.py encontrado")
    else:
        print("❌ arquivo settings.py não encontrado")
    
    # Teste 4: Verificar modelos
    if os.path.exists('mapa_eleitoral/models.py'):
        print("✅ models.py encontrado")
    else:
        print("❌ models.py não encontrado")
        
    print("\n📋 Estrutura básica verificada!")
    
except Exception as e:
    print(f"❌ Erro: {e}")