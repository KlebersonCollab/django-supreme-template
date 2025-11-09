# SSO (Social Authentication) Setup Guide

Este guia explica como configurar autenticação social (SSO) com Google, GitHub e Microsoft no Django Template.

## 📋 Pré-requisitos

1. Conta de desenvolvedor nos provedores (Google, GitHub, Microsoft)
2. Aplicação OAuth criada em cada provedor
3. Credenciais (Client ID e Client Secret) de cada provedor

## 🔗 Authorization Callback URLs

O Django Allauth cria automaticamente as URLs de callback. Use estas URLs ao configurar seus aplicativos OAuth:

### Desenvolvimento (localhost)

- **Google**: `http://localhost:8000/accounts/google/login/callback/`
- **GitHub**: `http://localhost:8000/accounts/github/login/callback/`
- **Microsoft**: `http://localhost:8000/accounts/microsoft/login/callback/`

### Produção

Substitua `localhost:8000` pelo seu domínio:

- **Google**: `https://seu-dominio.com/accounts/google/login/callback/`
- **GitHub**: `https://seu-dominio.com/accounts/github/login/callback/`
- **Microsoft**: `https://seu-dominio.com/accounts/microsoft/login/callback/`

## 🔧 Configuração por Provedor

### 1. Google OAuth2

#### Passo 1: Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá para **APIs & Services** → **Credentials**
4. Clique em **Create Credentials** → **OAuth client ID**
5. Configure:
   - **Application type**: Web application
   - **Name**: Django Supreme Template
   - **Authorized JavaScript origins**: 
     - `http://localhost:8000` (desenvolvimento)
     - `https://seu-dominio.com` (produção)
   - **Authorized redirect URIs**: 
     - `http://localhost:8000/accounts/google/login/callback/` (desenvolvimento)
     - `https://seu-dominio.com/accounts/google/login/callback/` (produção)
6. Copie o **Client ID** e **Client Secret**

#### Passo 2: Configurar no Django

**Opção A: Via Variáveis de Ambiente (Recomendado)**

1. Adicione as credenciais no arquivo `.env`:
   ```bash
   GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=seu-client-secret
   ```

2. Execute o script de setup:
   ```bash
   make setup-social-apps
   ```
   
   Ou manualmente:
   ```bash
   uv run python manage.py shell -c "exec(open('config/setup_social_apps.py').read())"
   ```

**Opção B: Via Django Admin (Manual)**

1. No Django Admin, vá para **Sites** → **Sites**
2. Configure o site com seu domínio (ou `localhost:8000` para desenvolvimento)
3. Vá para **Social Applications** → **Add Social Application**
4. Configure:
   - **Provider**: Google
   - **Name**: Google OAuth
   - **Client id**: (cole o Client ID)
   - **Secret key**: (cole o Client Secret)
   - **Sites**: Selecione o site configurado

#### Passo 3: Variáveis de Ambiente

Você também pode configurar via variáveis de ambiente no `.env`:

```bash
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
```

### 2. GitHub OAuth2

#### Passo 1: Criar OAuth App no GitHub

1. Acesse [GitHub Settings](https://github.com/settings/developers)
2. Clique em **OAuth Apps** → **New OAuth App**
3. Configure:
   - **Application name**: Django Supreme Template
   - **Homepage URL**: 
     - `http://localhost:8000` (desenvolvimento)
     - `https://seu-dominio.com` (produção)
   - **Authorization callback URL**: 
     - `http://localhost:8000/accounts/github/login/callback/` (desenvolvimento)
     - `https://seu-dominio.com/accounts/github/login/callback/` (produção)
4. Copie o **Client ID** e gere um **Client Secret**

#### Passo 2: Configurar no Django

**Opção A: Via Variáveis de Ambiente (Recomendado)**

1. Adicione as credenciais no arquivo `.env`:
   ```bash
   GITHUB_CLIENT_ID=seu-github-client-id
   GITHUB_CLIENT_SECRET=seu-github-client-secret
   ```

2. **IMPORTANTE**: Execute o script de setup para criar as Social Applications no banco:
   ```bash
   make setup-social-apps
   ```
   
   Este comando cria as Social Applications no Django Admin usando as variáveis de ambiente.

**Opção B: Via Django Admin (Manual)**

1. No Django Admin, vá para **Social Applications** → **Add Social Application**
2. Configure:
   - **Provider**: GitHub
   - **Name**: GitHub OAuth
   - **Client id**: (cole o Client ID)
   - **Secret key**: (cole o Client Secret)
   - **Sites**: Selecione o site configurado

#### Passo 3: Verificar Configuração

```bash
GITHUB_CLIENT_ID=seu-github-client-id
GITHUB_CLIENT_SECRET=seu-github-client-secret
```

### 3. Microsoft OAuth2 (Azure AD)

#### Passo 1: Registrar Aplicação no Azure Portal

1. Acesse [Azure Portal](https://portal.azure.com/)
2. Vá para **Azure Active Directory** → **App registrations** → **New registration**
3. Configure:
   - **Name**: Django Supreme Template
   - **Supported account types**: Accounts in any organizational directory and personal Microsoft accounts
   - **Redirect URI**: 
     - Type: Web
     - URI: `http://localhost:8000/accounts/microsoft/login/callback/` (desenvolvimento)
     - URI: `https://seu-dominio.com/accounts/microsoft/login/callback/` (produção)
4. Após criar, copie o **Application (client) ID**
5. Vá para **Certificates & secrets** → **New client secret**
6. Copie o **Value** do secret (não será mostrado novamente)

#### Passo 2: Configurar no Django

**Opção A: Via Variáveis de Ambiente (Recomendado)**

1. Adicione as credenciais no arquivo `.env`:
   ```bash
   MICROSOFT_CLIENT_ID=seu-azure-application-id
   MICROSOFT_CLIENT_SECRET=seu-azure-client-secret
   MICROSOFT_TENANT=common  # ou seu tenant ID específico
   ```

2. Execute o script de setup:
   ```bash
   make setup-social-apps
   ```

**Opção B: Via Django Admin (Manual)**

1. No Django Admin, vá para **Social Applications** → **Add Social Application**
2. Configure:
   - **Provider**: Microsoft
   - **Name**: Microsoft OAuth
   - **Client id**: (cole o Application ID)
   - **Secret key**: (cole o Client Secret)
   - **Sites**: Selecione o site configurado

#### Passo 3: Verificar Configuração

```bash
MICROSOFT_CLIENT_ID=seu-azure-application-id
MICROSOFT_CLIENT_SECRET=seu-azure-client-secret
MICROSOFT_TENANT=common  # ou seu tenant ID específico
```

## 🎯 URLs Disponíveis

Após configurar, você pode acessar:

### Portal SSO (Web)
- **Login**: `/accounts/login/`
- **Google Login**: `/accounts/google/login/`
- **GitHub Login**: `/accounts/github/login/`
- **Microsoft Login**: `/accounts/microsoft/login/`

### Admin com SSO
- **Admin Login**: `/admin/login/` (redireciona automaticamente para `/accounts/login/`)

### API SSO (Mobile)
- **SSO Authenticate**: `POST /api/sso/authenticate/`

## ⚠️ Troubleshooting

### Erro "Too Many Requests" do GitHub

Se você receber um erro "too many requests" ou "rate limit" ao tentar fazer login com GitHub:

1. **Aguarde alguns minutos**: O GitHub limita requisições OAuth para prevenir abuso
2. **Verifique suas credenciais**: Certifique-se de que `GITHUB_CLIENT_ID` e `GITHUB_CLIENT_SECRET` estão corretos
3. **Verifique o callback URL**: O callback URL no GitHub deve ser exatamente: `http://localhost:8000/accounts/github/login/callback/`
4. **Limite de requisições**: O GitHub permite aproximadamente 5000 requisições por hora por IP. Se você estiver testando muito, pode atingir esse limite

**Solução temporária**: Use outro provider (Google ou Microsoft) enquanto aguarda o rate limit do GitHub resetar.

## ✅ Verificação

Após configurar:

1. Acesse `/admin/login/` (será redirecionado para `/accounts/login/`)
2. Você deve ver os botões de login social
3. Clique em um botão e verifique se redireciona corretamente
4. Após autenticar, você deve ser redirecionado para `/admin/`

## 🔒 Segurança

### Produção

- ✅ Use HTTPS em produção
- ✅ Configure `ALLOWED_HOSTS` corretamente
- ✅ Use variáveis de ambiente para secrets
- ✅ Configure `DJANGO_SECRET_KEY` seguro
- ✅ Desabilite `DEBUG=False` em produção

### Callback URLs

- ✅ Use URLs exatas (case-sensitive)
- ✅ Configure tanto desenvolvimento quanto produção
- ✅ Verifique se o domínio está em `ALLOWED_HOSTS`

## 📝 Notas Importantes

1. **Site ID**: O Django Allauth requer um Site configurado. O Site ID padrão é 1.
2. **Domínio**: Certifique-se de que o domínio no Django Admin (Sites) corresponde ao domínio usado nas URLs de callback.
3. **HTTPS**: Em produção, sempre use HTTPS. Os provedores OAuth geralmente exigem HTTPS.
4. **Scopes**: Os scopes padrão já estão configurados para obter email e perfil do usuário.

## 🐛 Troubleshooting

### Erro: "Redirect URI mismatch"

- Verifique se a URL de callback está exatamente igual no provedor OAuth
- Certifique-se de que está usando `http://` ou `https://` corretamente
- Verifique se o domínio está em `ALLOWED_HOSTS`

### Erro: "Invalid client"

- Verifique se o Client ID e Client Secret estão corretos
- Certifique-se de que copiou os valores completos (sem espaços)

### Login social não aparece

- Verifique se a Social Application está configurada no Django Admin
- Certifique-se de que o Site está selecionado na Social Application
- Verifique se os providers estão em `INSTALLED_APPS`

## 📚 Referências

- [Django Allauth Documentation](https://docs.allauth.org/)
- [Google OAuth2 Setup](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth2 Setup](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps)
- [Microsoft Azure AD Setup](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app)

