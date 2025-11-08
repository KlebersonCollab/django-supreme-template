# Rate Limiting Configuration

O template Django inclui rate limiting configurado usando o sistema de throttling do Django REST Framework.

## Como Funciona

O rate limiting é aplicado automaticamente a todos os endpoints da API usando:

- **AnonRateThrottle**: Para usuários anônimos (não autenticados)
- **UserRateThrottle**: Para usuários autenticados

## Configuração

### Variáveis de Ambiente

```bash
# Limite para usuários anônimos
RATE_LIMIT_ANON=100/hour

# Limite para usuários autenticados
RATE_LIMIT_USER=1000/hour

# Limite de burst (para endpoints específicos)
RATE_LIMIT_BURST=10/minute
```

### Formatos Suportados

- `number/second` - Por segundo
- `number/minute` - Por minuto
- `number/hour` - Por hora
- `number/day` - Por dia

### Valores Padrão

- **Anônimos**: 100 requisições por hora
- **Autenticados**: 1000 requisições por hora
- **Burst**: 10 requisições por minuto

## Uso em Endpoints Específicos

Para aplicar rate limiting customizado em endpoints específicos:

```python
from rest_framework.decorators import throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

@api_view(["GET"])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def my_endpoint(request):
    # Seu código aqui
    pass
```

## Respostas de Rate Limit

Quando o limite é excedido, a API retorna:

```json
{
  "detail": "Request was throttled. Expected available in X seconds."
}
```

Com status code `429 Too Many Requests`.

## Headers de Resposta

A API inclui headers informativos sobre o rate limit:

- `X-RateLimit-Limit`: Limite total permitido
- `X-RateLimit-Remaining`: Requisições restantes
- `X-RateLimit-Reset`: Timestamp de reset do limite
- `Retry-After`: Segundos até poder fazer nova requisição

## Exemplos

### Limite Padrão (Anônimos)

```bash
# 100 requisições por hora para usuários não autenticados
curl http://localhost:8000/api/health/
```

### Limite para Autenticados

```bash
# 1000 requisições por hora para usuários autenticados
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/user/
```

## Customização Avançada

Para criar throttles customizados, crie uma classe em `config/throttles.py`:

```python
from rest_framework.throttling import UserRateThrottle

class BurstRateThrottle(UserRateThrottle):
    scope = 'burst'
```

E use nos endpoints:

```python
@throttle_classes([BurstRateThrottle])
def my_endpoint(request):
    pass
```

## Desabilitar Rate Limiting

Para desabilitar rate limiting em um endpoint específico:

```python
from rest_framework.throttling import UserRateThrottle

class NoThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        return True

@throttle_classes([NoThrottle])
def my_endpoint(request):
    pass
```

Ou remova `DEFAULT_THROTTLE_CLASSES` de `REST_FRAMEWORK` em `settings.py`.

## Monitoramento

O rate limiting usa o cache configurado (Redis ou DummyCache) para armazenar contadores.

Para monitorar rate limits:
- Verifique os headers de resposta
- Monitore logs para requisições 429
- Use ferramentas de monitoring (Sentry, etc.)

## Boas Práticas

1. **Ajuste limites por ambiente**:
   - Desenvolvimento: limites mais altos
   - Produção: limites mais restritivos

2. **Diferencie por tipo de usuário**:
   - Usuários anônimos: limites menores
   - Usuários autenticados: limites maiores
   - Usuários premium: limites ainda maiores

3. **Endpoints críticos**:
   - Aplique limites mais restritivos
   - Use burst limits para prevenir abuso

4. **Monitoramento**:
   - Acompanhe requisições 429
   - Ajuste limites baseado em uso real

