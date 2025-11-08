# Secrets Management Integration

O template Django inclui suporte para múltiplos provedores de gerenciamento de secrets, permitindo gerenciar credenciais e configurações sensíveis de forma segura.

## Provedores Suportados

1. **AWS Secrets Manager** - Amazon Web Services
2. **Google Cloud Secret Manager** - Google Cloud Platform
3. **Azure Key Vault** - Microsoft Azure
4. **HashiCorp Vault** - Vault open-source/enterprise
5. **Environment Variables** - Fallback padrão

## Configuração Rápida

### 1. Escolher Provedor

Configure o provedor via variável de ambiente:

```bash
SECRETS_PROVIDER=aws      # AWS Secrets Manager
SECRETS_PROVIDER=gcp      # Google Cloud Secret Manager
SECRETS_PROVIDER=azure    # Azure Key Vault
SECRETS_PROVIDER=vault    # HashiCorp Vault
SECRETS_PROVIDER=env      # Environment Variables (padrão)
```

### 2. Instalar Dependências

Instale apenas as dependências do provedor que você vai usar:

```bash
# AWS Secrets Manager (boto3 já está incluído)
# Não precisa instalar nada adicional

# Google Cloud Secret Manager
uv pip install google-cloud-secret-manager

# Azure Key Vault
uv pip install azure-keyvault-secrets azure-identity

# HashiCorp Vault
uv pip install hvac
```

## Configuração por Provedor

### AWS Secrets Manager

```bash
# Configuração
SECRETS_PROVIDER=aws
AWS_SECRETS_REGION=us-east-1  # ou use AWS_REGION
AWS_ACCESS_KEY_ID=your-access-key  # ou use IAM role
AWS_SECRET_ACCESS_KEY=your-secret-key  # ou use IAM role

# Armazenar secret
aws secretsmanager create-secret \
  --name DJANGO_SECRET_KEY \
  --secret-string "your-secret-key-value"

# Ou como JSON (múltiplos valores)
aws secretsmanager create-secret \
  --name django-config \
  --secret-string '{"SECRET_KEY":"value1","DB_PASSWORD":"value2"}'
```

**Uso no código**:
```python
from config.secrets import get_secret

# Buscar secret simples
secret_key = get_secret("DJANGO_SECRET_KEY")

# Buscar secret JSON (múltiplos valores)
from config.secrets import get_secrets_dict
config = get_secrets_dict("django-config")
db_password = config.get("DB_PASSWORD")
```

### Google Cloud Secret Manager

```bash
# Configuração
SECRETS_PROVIDER=gcp
GCP_PROJECT_ID=my-project-id
# Ou use GOOGLE_CLOUD_PROJECT

# Autenticação (escolha uma):
# 1. Service Account Key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# 2. Application Default Credentials (GCP environments)
# Já configurado automaticamente no GCP

# Criar secret
gcloud secrets create DJANGO_SECRET_KEY --data-file=- <<< "your-secret-value"
```

**Uso no código**:
```python
from config.secrets import get_secret

secret_key = get_secret("DJANGO_SECRET_KEY")
```

### Azure Key Vault

```bash
# Configuração
SECRETS_PROVIDER=azure
AZURE_KEY_VAULT_URL=https://my-vault.vault.azure.net/

# Autenticação (escolha uma):
# 1. Managed Identity (Azure environments)
# Já configurado automaticamente no Azure

# 2. Service Principal
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT_ID=your-tenant-id

# 3. Azure CLI
az login

# Criar secret
az keyvault secret set \
  --vault-name my-vault \
  --name DJANGO_SECRET_KEY \
  --value "your-secret-value"
```

**Uso no código**:
```python
from config.secrets import get_secret

secret_key = get_secret("DJANGO_SECRET_KEY")
```

### HashiCorp Vault

```bash
# Configuração
SECRETS_PROVIDER=vault
VAULT_ADDR=http://127.0.0.1:8200  # ou https://vault.example.com
VAULT_TOKEN=your-vault-token
VAULT_MOUNT_POINT=secret  # Padrão: secret
VAULT_KV_VERSION=2  # 1 ou 2 (padrão: 2)

# Criar secret (KV v2)
vault kv put secret/django DJANGO_SECRET_KEY=your-secret-value

# Criar secret (KV v1)
vault kv put secret/django DJANGO_SECRET_KEY=your-secret-value
```

**Uso no código**:
```python
from config.secrets import get_secret

# Para KV v2: secret_name = "django"
# Para KV v1: secret_name = "django"
secret_key = get_secret("django")  # Retorna DJANGO_SECRET_KEY se único, ou JSON
```

## Uso no Django Settings

O template já está configurado para usar secrets management automaticamente:

```python
# config/settings.py
# SECRET_KEY é automaticamente buscado do secrets manager se configurado
```

### Buscar Outros Secrets

```python
# Em config/settings.py ou qualquer lugar
from config.secrets import get_secret, get_secrets_dict

# Buscar secret individual
DB_PASSWORD = get_secret("DB_PASSWORD", default="fallback-password")

# Buscar múltiplos secrets de uma vez (JSON)
db_config = get_secrets_dict("database-config")
DB_NAME = db_config.get("DB_NAME", "default_db")
DB_USER = db_config.get("DB_USER", "default_user")
DB_PASSWORD = db_config.get("DB_PASSWORD", "default_password")
```

## Exemplos de Uso

### Exemplo 1: Database Credentials

```python
# config/settings.py
from config.secrets import get_secrets_dict

# Buscar credenciais do banco de dados
db_secrets = get_secrets_dict("database-credentials")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": db_secrets.get("DB_NAME", os.environ.get("DB_NAME", "")),
        "USER": db_secrets.get("DB_USER", os.environ.get("DB_USER", "")),
        "PASSWORD": db_secrets.get("DB_PASSWORD", os.environ.get("DB_PASSWORD", "")),
        "HOST": db_secrets.get("DB_HOST", os.environ.get("DB_HOST", "localhost")),
        "PORT": db_secrets.get("DB_PORT", os.environ.get("DB_PORT", "5432")),
    }
}
```

### Exemplo 2: API Keys

```python
# config/settings.py
from config.secrets import get_secret

# Buscar API keys individuais
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID", default=os.environ.get("GOOGLE_CLIENT_ID", ""))
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET", default=os.environ.get("GOOGLE_CLIENT_SECRET", ""))
```

### Exemplo 3: JWT Signing Key

```python
# config/settings.py
from config.secrets import get_secret

# Buscar JWT signing key
JWT_SIGNING_KEY = get_secret("JWT_SIGNING_KEY", default=SECRET_KEY)
```

## Fallback e Segurança

### Ordem de Prioridade

1. **Secrets Manager** (se `SECRETS_PROVIDER != "env"`)
2. **Environment Variables** (fallback)
3. **Default value** (último recurso)

### Tratamento de Erros

O módulo de secrets trata erros graciosamente:

- Se o secret não for encontrado, retorna `default` ou `None`
- Erros são logados mas não quebram a aplicação
- Fallback automático para environment variables

### Segurança

1. **Nunca commite secrets**: Use `.gitignore` para arquivos de secrets
2. **Use IAM/Roles**: Configure permissões adequadas no provedor
3. **Rotação**: Configure rotação automática de secrets quando possível
4. **Auditoria**: Monitore acesso a secrets via logs do provedor
5. **Princípio do menor privilégio**: Dê apenas permissões necessárias

## Migração de Environment Variables

Para migrar de environment variables para secrets manager:

1. **Criar secrets no provedor**:
   ```bash
   # AWS
   aws secretsmanager create-secret --name django-config --secret-string '{"SECRET_KEY":"...","DB_PASSWORD":"..."}'
   
   # GCP
   echo -n "secret-value" | gcloud secrets create SECRET_NAME --data-file=-
   
   # Azure
   az keyvault secret set --vault-name vault --name secret --value "value"
   
   # Vault
   vault kv put secret/django key=value
   ```

2. **Configurar provedor**:
   ```bash
   export SECRETS_PROVIDER=aws  # ou gcp, azure, vault
   ```

3. **Atualizar código** (opcional):
   ```python
   # Antes
   SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
   
   # Depois (já funciona automaticamente)
   # SECRET_KEY já busca do secrets manager se configurado
   ```

## Troubleshooting

### Erro: "Secret not found"

- Verifique se o secret existe no provedor
- Verifique permissões de acesso
- Verifique nome do secret (case-sensitive em alguns provedores)

### Erro: "Authentication failed"

- Verifique credenciais (AWS keys, GCP service account, Azure credentials, Vault token)
- Verifique IAM roles/permissions
- Verifique network access (firewall, VPC, etc.)

### Performance

- Secrets são cacheados em memória (não há cache persistente)
- Para alta performance, considere usar environment variables em desenvolvimento
- Use secrets manager apenas em produção/staging

## Boas Práticas

1. **Desenvolvimento**: Use environment variables (`.env`)
2. **Staging/Produção**: Use secrets manager
3. **Rotação**: Configure rotação automática
4. **Backup**: Mantenha backup de secrets críticos
5. **Documentação**: Documente quais secrets são necessários
6. **Testes**: Use mocks/stubs para testes

## Referências

- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager/docs)
- [Azure Key Vault](https://docs.microsoft.com/azure/key-vault/)
- [HashiCorp Vault](https://www.vaultproject.io/docs)

