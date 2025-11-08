# Sentry Monitoring Configuration

O template Django inclui suporte opcional para Sentry, uma plataforma de error tracking e performance monitoring.

## Configuração

### 1. Obter DSN do Sentry

1. Crie uma conta em [sentry.io](https://sentry.io)
2. Crie um novo projeto (Django)
3. Copie o DSN fornecido

### 2. Configurar Variáveis de Ambiente

```bash
# Sentry DSN (obrigatório para habilitar)
SENTRY_DSN=https://your-dsn@sentry.io/project-id

# Opcional: Configurações avançadas
SENTRY_ENVIRONMENT=production  # ou development, staging
SENTRY_RELEASE=my-app@1.0.0    # Versão da aplicação
SENTRY_TRACES_SAMPLE_RATE=0.1  # 10% das transações (0.0 a 1.0)
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% dos profiles
SENTRY_SEND_DEFAULT_PII=True  # Enviar dados pessoais (GDPR)
```

### 3. Habilitar Sentry

O Sentry é habilitado automaticamente quando `SENTRY_DSN` está configurado.

## O que é Monitorado

### Erros Automáticos
- Exceções não tratadas
- Erros de views
- Erros de middleware
- Erros de templates
- Erros de database

### Performance
- Tempo de resposta de views
- Queries de database
- Operações de cache
- Middleware execution
- Signal handlers

### Contexto Automático
- Request headers
- User information (se autenticado)
- URL e método HTTP
- Query parameters
- Stack traces

## Uso em Código

### Capturar Erro Manualmente

```python
import sentry_sdk

try:
    # Seu código
    result = risky_operation()
except Exception as e:
    sentry_sdk.capture_exception(e)
    # Ou
    sentry_sdk.capture_message("Algo deu errado", level="error")
```

### Adicionar Contexto

```python
import sentry_sdk

# Adicionar tags
sentry_sdk.set_tag("feature", "payment")
sentry_sdk.set_tag("environment", "production")

# Adicionar contexto customizado
sentry_sdk.set_context("payment", {
    "amount": 100.00,
    "currency": "USD",
    "method": "credit_card"
})

# Adicionar usuário
sentry_sdk.set_user({
    "id": user.id,
    "email": user.email,
    "username": user.username
})
```

### Performance Monitoring

```python
import sentry_sdk

# Rastrear operação específica
with sentry_sdk.start_span(op="payment.process", description="Process payment"):
    # Seu código de pagamento
    process_payment()
```

### Breadcrumbs

```python
import sentry_sdk

# Adicionar breadcrumb (evento que leva ao erro)
sentry_sdk.add_breadcrumb(
    message="User clicked button",
    level="info",
    category="ui",
    data={"button": "submit"}
)
```

## Configurações Avançadas

### Sample Rates

```bash
# Capturar 100% das transações (cuidado com custo)
SENTRY_TRACES_SAMPLE_RATE=1.0

# Capturar apenas 1% (economia)
SENTRY_TRACES_SAMPLE_RATE=0.01
```

### Filtros Customizados

Edite `config/settings.py` para adicionar filtros:

```python
def before_send(event, hint):
    # Filtrar eventos específicos
    if event.get("logger") == "django.request":
        return None  # Não enviar
    return event

sentry_sdk.init(
    dsn=SENTRY_DSN,
    before_send=before_send,
)
```

### Ambientes

```bash
# Desenvolvimento
SENTRY_ENVIRONMENT=development

# Staging
SENTRY_ENVIRONMENT=staging

# Produção
SENTRY_ENVIRONMENT=production
```

## Desabilitar Sentry

Para desabilitar, simplesmente não configure `SENTRY_DSN` ou remova a variável de ambiente.

## Integração com Logging

O Sentry integra automaticamente com o sistema de logging do Django:

- Logs de nível ERROR são enviados como eventos
- Logs de nível INFO+ são capturados como breadcrumbs
- Stack traces são incluídos automaticamente

## Performance Monitoring

### Transações

Todas as views são automaticamente rastreadas como transações:

- Tempo de resposta
- Status code
- Database queries
- Cache operations

### Profiles

Para análise de performance detalhada:

```bash
SENTRY_PROFILES_SAMPLE_RATE=0.1  # 10% dos profiles
```

## Alertas

Configure alertas no Sentry Dashboard:

1. Vá para Settings → Alerts
2. Crie regras de alerta:
   - Erros novos
   - Taxa de erro alta
   - Performance degradada
   - Thresholds customizados

## Boas Práticas

1. **Não capture em DEBUG**: Sentry não envia eventos em modo DEBUG
2. **Use sample rates**: Ajuste para não sobrecarregar
3. **Filtre ruído**: Configure `before_send` para filtrar eventos irrelevantes
4. **Contexto rico**: Adicione contexto útil para debugging
5. **Releases**: Configure releases para rastrear versões
6. **Ambientes**: Use diferentes ambientes para dev/staging/prod

## Troubleshooting

### Sentry não está enviando eventos

1. Verifique se `SENTRY_DSN` está configurado
2. Verifique se não está em modo DEBUG
3. Verifique logs do Django para erros do Sentry
4. Teste com `sentry_sdk.capture_message("test")`

### Muitos eventos

1. Reduza `SENTRY_TRACES_SAMPLE_RATE`
2. Configure `before_send` para filtrar
3. Ajuste níveis de logging

### Performance impact

1. Use sample rates menores
2. Desabilite profiling em produção
3. Configure filtros para reduzir volume

