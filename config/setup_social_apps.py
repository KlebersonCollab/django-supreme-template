"""
Script para configurar Social Applications via variáveis de ambiente.

Este script cria Social Applications no Django Admin usando variáveis de ambiente,
evitando a necessidade de configurar manualmente no admin.

Uso:
    uv run python manage.py shell < config/setup_social_apps.py
    ou
    uv run python manage.py shell -c "exec(open('config/setup_social_apps.py').read())"
"""

import os
from pathlib import Path
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Carregar variáveis de ambiente do arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR / ".env"

if env_file.exists():
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Ignora linhas vazias, comentários e linhas sem =
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                # Remove aspas se houver
                value = value.strip().strip('"').strip("'")
                # Remove espaços extras
                value = value.strip()
                # Só define se não estiver vazio
                if value:
                    os.environ[key] = value

# Obter site atual
site = Site.objects.get_current()

# Google
google_client_id = os.environ.get("GOOGLE_CLIENT_ID")
google_secret = os.environ.get("GOOGLE_CLIENT_SECRET")

if google_client_id and google_secret:
    # Remove todas as duplicatas primeiro
    SocialApp.objects.filter(provider="google").delete()
    # Cria nova e associa ao site em uma única operação
    app = SocialApp.objects.create(
        provider="google",
        name="Google OAuth",
        client_id=google_client_id,
        secret=google_secret,
    )
    app.sites.add(site)  # Adiciona o site
    app.save()  # Salva explicitamente
    print(f"✅ Google OAuth configurado: {app.name} (ID: {app.client_id[:20]}...)")
    # Verificar se foi associado corretamente
    if site in app.sites.all():
        print(f"   ✅ Site associado corretamente")
    else:
        print(f"   ❌ ERRO: Site não foi associado!")
else:
    print("⚠️  GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET não configurados")

# GitHub
github_client_id = os.environ.get("GITHUB_CLIENT_ID")
github_secret = os.environ.get("GITHUB_CLIENT_SECRET")

if github_client_id and github_secret:
    # Remove todas as duplicatas primeiro
    SocialApp.objects.filter(provider="github").delete()
    # Cria nova e associa ao site em uma única operação
    app = SocialApp.objects.create(
        provider="github",
        name="GitHub OAuth",
        client_id=github_client_id,
        secret=github_secret,
    )
    app.sites.add(site)  # Adiciona o site
    app.save()  # Salva explicitamente
    print(f"✅ GitHub OAuth configurado: {app.name} (ID: {app.client_id[:20]}...)")
    # Verificar se foi associado corretamente
    if site in app.sites.all():
        print(f"   ✅ Site associado corretamente")
    else:
        print(f"   ❌ ERRO: Site não foi associado!")
else:
    print("⚠️  GITHUB_CLIENT_ID e GITHUB_CLIENT_SECRET não configurados")

# Microsoft
microsoft_client_id = os.environ.get("MICROSOFT_CLIENT_ID")
microsoft_secret = os.environ.get("MICROSOFT_CLIENT_SECRET")

if microsoft_client_id and microsoft_secret:
    # Remove todas as duplicatas primeiro
    SocialApp.objects.filter(provider="microsoft").delete()
    # Cria nova e associa ao site em uma única operação
    app = SocialApp.objects.create(
        provider="microsoft",
        name="Microsoft OAuth",
        client_id=microsoft_client_id,
        secret=microsoft_secret,
    )
    app.sites.add(site)  # Adiciona o site
    app.save()  # Salva explicitamente
    print(f"✅ Microsoft OAuth configurado: {app.name} (ID: {app.client_id[:20]}...)")
    # Verificar se foi associado corretamente
    if site in app.sites.all():
        print(f"   ✅ Site associado corretamente")
    else:
        print(f"   ❌ ERRO: Site não foi associado!")
else:
    print("⚠️  MICROSOFT_CLIENT_ID e MICROSOFT_CLIENT_SECRET não configurados")

print("\n📝 Nota: Configure as variáveis de ambiente no arquivo .env")
print("   Veja docs/SSO_SETUP.md para instruções completas")

