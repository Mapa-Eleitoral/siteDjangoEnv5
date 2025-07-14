#!/usr/bin/env python3
"""
Script de emergência para deploy sem multi-database
Remove configurações de banco blog para funcionar apenas com default
"""

import os
import shutil

def create_emergency_deploy():
    print("🚨 Criando versão de emergência...")
    
    # Backup atual
    backup_dir = "backup_multidatabase"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Fazer backup dos arquivos alterados
    files_to_backup = [
        "siteDjango/settings.py",
        "siteDjango/db_router.py",
        "mapa_eleitoral/models.py",
        "mapa_eleitoral/views.py"
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, f"{backup_dir}/{os.path.basename(file)}")
    
    print("✅ Backup criado")
    
    # Reverter para versão sem multi-database
    print("🔄 Revertendo para banco único...")
    
    # Remover router
    if os.path.exists("siteDjango/db_router.py"):
        os.remove("siteDjango/db_router.py")
    
    print("✅ Versão de emergência criada")
    print("📋 Para deploy manual:")
    print("1. Faça upload dos arquivos no GitHub")
    print("2. Railway fará auto-deploy")
    print("3. Site voltará a funcionar")

if __name__ == "__main__":
    create_emergency_deploy()