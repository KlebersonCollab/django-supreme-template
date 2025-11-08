# API Versioning Guide

O template Django suporta versionamento de API usando URL path versioning.

## Estrutura

```
/api/v1/          # Versão 1 da API
/api/v2/          # Versão 2 da API (quando criada)
/api/             # Endpoints legacy (mapeiam para v1)
```

## Endpoints Versionados

### Versão 1 (v1)

- `POST /api/v1/token/` - Obter JWT tokens
- `POST /api/v1/token/refresh/` - Renovar token
- `POST /api/v1/token/verify/` - Verificar token
- `POST /api/v1/sso/authenticate/` - SSO Mobile
- `GET /api/v1/user/` - Info do usuário
- `GET /api/v1/health/` - Health check

### Endpoints Legacy (Backward Compatibility)

Os endpoints sem versão mapeiam para v1:

- `POST /api/token/` → v1
- `POST /api/token/refresh/` → v1
- `POST /api/token/verify/` → v1
- `POST /api/sso/authenticate/` → v1
- `GET /api/user/` → v1
- `GET /api/health/` → v1

## Criando Nova Versão (v2)

### 1. Criar arquivo `config/api_v2.py`

```python
# config/api_v2.py
from django.urls import path
from config.api_views import api_health_check, api_user_info
from config.sso_auth import sso_authenticate

app_name = "api_v2"

urlpatterns = [
    # Endpoints v2 (pode ter mudanças na API)
    path("sso/authenticate/", sso_authenticate, name="sso_authenticate"),
    path("user/", api_user_info, name="api_user_info"),
    path("health/", api_health_check, name="api_health_check"),
]
```

### 2. Adicionar rota em `config/urls.py`

```python
# config/urls.py
from config import api_v2  # Import new version

urlpatterns = [
    # ... existing patterns ...
    path("api/v2/", include("config.api_v2")),
    # ... rest of patterns ...
]
```

### 3. Atualizar `settings.py`

```python
# config/settings.py
REST_FRAMEWORK["ALLOWED_VERSIONS"] = ["v1", "v2", "v3"]  # Add new version
```

## Boas Práticas

1. **Mantenha compatibilidade**: Endpoints legacy devem continuar funcionando
2. **Documente mudanças**: Use CHANGELOG.md para documentar breaking changes
3. **Deprecation warnings**: Adicione warnings em endpoints antigos
4. **Testes**: Teste todas as versões
5. **Swagger**: Atualize documentação para cada versão

## Exemplo de Migração

### v1 → v2

```python
# config/api_v2.py
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def api_user_info_v2(request):
    """
    Versão 2 do endpoint de usuário.
    
    Mudanças:
    - Adiciona campo 'preferences'
    - Remove campo 'legacy_field'
    """
    return Response({
        "user_id": request.user.id,
        "email": request.user.email,
        "preferences": {},  # Novo campo
        # legacy_field removido
    })
```

## Versionamento em Views

Para acessar a versão na view:

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(["GET"])
def my_view(request):
    version = request.version  # 'v1', 'v2', etc.
    
    if version == 'v2':
        # Lógica para v2
        return Response({"version": "v2", "data": "..."})
    else:
        # Lógica para v1
        return Response({"version": "v1", "data": "..."})
```

## Documentação Swagger

O Swagger UI mostra todas as versões disponíveis. Acesse:

- `/api/schema/swagger-ui/` - Interface Swagger
- `/api/schema/redoc/` - Documentação ReDoc

## Recomendações

1. **Não quebre compatibilidade**: Mantenha v1 funcionando
2. **Deprecation period**: Dê tempo para clientes migrarem
3. **Versionamento semântico**: Use v1, v2, v3 para breaking changes
4. **Documentação**: Documente todas as mudanças entre versões

