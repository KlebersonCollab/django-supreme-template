# Database Connection Pooling

O template Django suporta connection pooling para PostgreSQL usando `django-db-connection-pool`.

## Quando Usar

Connection pooling é útil quando:
- Você tem alta concorrência de requisições
- Está usando PostgreSQL em produção
- Quer reduzir overhead de conexões
- Tem muitas requisições simultâneas

**Não é necessário para**:
- SQLite (não suporta pooling)
- Aplicações com baixo tráfego
- Desenvolvimento local

## Configuração

### 1. Habilitar Pooling

```bash
# Usar PostgreSQL
DB_ENGINE=django.db.backends.postgresql

# Habilitar connection pooling
USE_DB_POOL=True

# Configurações do banco
DB_NAME=my_database
DB_USER=my_user
DB_PASSWORD=my_password
DB_HOST=localhost
DB_PORT=5432

# Configurações do pool (opcional)
DB_POOL_MAX_CONNS=20  # Máximo de conexões no pool
DB_POOL_MIN_CONNS=5   # Mínimo de conexões no pool
```

### 2. Instalar Dependência

O `django-db-connection-pool` já está nas dependências. Se não estiver instalado:

```bash
uv sync
```

## Como Funciona

### Sem Pooling (Padrão)

```
Request 1 → Nova conexão → Database
Request 2 → Nova conexão → Database
Request 3 → Nova conexão → Database
```

Cada requisição cria uma nova conexão, causando overhead.

### Com Pooling

```
Request 1 → Pool → Conexão reutilizada → Database
Request 2 → Pool → Conexão reutilizada → Database
Request 3 → Pool → Nova conexão (se necessário) → Database
```

Conexões são reutilizadas do pool, reduzindo overhead.

## Configurações do Pool

### MAX_CONNS (Máximo de Conexões)

```bash
DB_POOL_MAX_CONNS=20  # Padrão: 20
```

- Controla o número máximo de conexões simultâneas
- Ajuste baseado na capacidade do servidor PostgreSQL
- Recomendado: 10-50 para a maioria dos casos

### MIN_CONNS (Mínimo de Conexões)

```bash
DB_POOL_MIN_CONNS=5  # Padrão: 5
```

- Número mínimo de conexões mantidas no pool
- Conexões são criadas na inicialização
- Útil para manter conexões "quentes"

## Monitoramento

### Verificar Conexões Ativas

```sql
-- No PostgreSQL
SELECT count(*) FROM pg_stat_activity WHERE datname = 'your_database';
```

### Verificar Pool Status

O pool gerencia conexões automaticamente. Para debugging:

```python
from django.db import connection

# Verificar conexão atual
print(connection.connection)
```

## Performance

### Benefícios

- **Redução de overhead**: Menos criação/destruição de conexões
- **Melhor throughput**: Conexões reutilizadas são mais rápidas
- **Controle de recursos**: Limita número de conexões simultâneas

### Trade-offs

- **Memória**: Pool mantém conexões em memória
- **Complexidade**: Mais uma camada de configuração
- **Debugging**: Pode ser mais difícil debugar problemas de conexão

## Troubleshooting

### Erro: "too many connections"

Aumente `DB_POOL_MAX_CONNS` ou verifique limites do PostgreSQL:

```sql
-- Verificar limite do PostgreSQL
SHOW max_connections;
```

### Conexões não sendo reutilizadas

- Verifique se `USE_DB_POOL=True`
- Verifique logs do Django
- Verifique se `django-db-connection-pool` está instalado

### Performance não melhorou

- Connection pooling ajuda principalmente com alta concorrência
- Para baixo tráfego, o overhead pode não valer a pena
- Considere otimizar queries primeiro

## Desabilitar Pooling

Para desabilitar pooling mas continuar usando PostgreSQL:

```bash
DB_ENGINE=django.db.backends.postgresql
USE_DB_POOL=False  # ou não defina a variável
```

## Boas Práticas

1. **Ajuste baseado em carga**: Monitore e ajuste `MAX_CONNS`
2. **Não exagere**: Muitas conexões podem sobrecarregar o DB
3. **Monitore**: Acompanhe uso de conexões
4. **Teste**: Teste em ambiente similar à produção
5. **Documente**: Documente configurações escolhidas

## Exemplo de Configuração por Ambiente

### Desenvolvimento

```bash
USE_DB_POOL=False  # Não necessário para dev
```

### Staging

```bash
USE_DB_POOL=True
DB_POOL_MAX_CONNS=10
DB_POOL_MIN_CONNS=2
```

### Produção

```bash
USE_DB_POOL=True
DB_POOL_MAX_CONNS=20
DB_POOL_MIN_CONNS=5
```

