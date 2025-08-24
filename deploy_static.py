#!/usr/bin/env python
"""
Script para deployment de arquivos estáticos do FinanPy.
Execute este script para coletar e preparar todos os arquivos estáticos.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    """Executa os comandos necessários para deployment de static files."""
    
    # Configura o ambiente Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    
    print("🚀 Iniciando deployment de arquivos estáticos...")
    
    # Remove arquivos estáticos antigos
    print("🧹 Limpando arquivos estáticos antigos...")
    execute_from_command_line(['manage.py', 'collectstatic', '--clear', '--noinput'])
    
    # Coleta todos os arquivos estáticos
    print("📦 Coletando arquivos estáticos...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("✅ Deployment de arquivos estáticos concluído com sucesso!")
    print(f"📁 Arquivos estáticos coletados em: {os.path.join(os.getcwd(), 'staticfiles')}")
    
    # Verifica se os arquivos principais existem
    static_files_to_check = [
        'staticfiles/css/custom.css',
        'staticfiles/js/main.js',
        'staticfiles/admin/css/base.css'
    ]
    
    print("\n🔍 Verificando arquivos principais...")
    for file_path in static_files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - ARQUIVO NÃO ENCONTRADO")
    
    print("\n📋 Próximos passos para produção:")
    print("1. Configure seu servidor web (Apache/Nginx) para servir arquivos estáticos")
    print("2. Aponte STATIC_ROOT para o diretório correto do servidor")
    print("3. Use settings_production.py com ManifestStaticFilesStorage")
    print("4. Configure HTTPS e headers de segurança")

if __name__ == '__main__':
    main()