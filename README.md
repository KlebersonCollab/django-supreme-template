# Django Template

A modern Django project template with Python 3.11+, Django 5.2+, and `uv` for dependency management.

## Features

- **Django 5.2.8**: Latest stable version of Django
- **Python 3.11+**: Modern Python features and performance
- **UV**: Fast Python package manager
- **Type Hints**: Full type checking with mypy and django-stubs
- **Code Quality**: Ruff for linting and formatting
- **Testing**: pytest-django with 64.21% coverage (44 tests passing, 3 skipped)
- **SQLite**: Default database (easily configurable for PostgreSQL/MySQL)
- **CORS**: Cross-origin resource sharing configured
- **API Docs**: OpenAPI/Swagger documentation
- **Docker**: Production-ready Dockerfile and docker-compose
- **CI/CD**: GitHub Actions workflows
- **Logging**: Structured logging with rotation
- **Security**: Security headers, CORS, JWT authentication, Rate Limiting
- **Secrets Management**: AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, HashiCorp Vault
- **API Versioning**: Support for multiple API versions (/api/v1/, /api/v2/)
- **Database Pooling**: Connection pooling for PostgreSQL
- **Monitoring**: Sentry integration for error tracking and performance

## Requirements

- Python 3.11 or higher
- [UV](https://github.com/astral-sh/uv) package manager

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

This will:
- Create a virtual environment (`.venv/`)
- Install Django and all dependencies
- Install development dependencies (pytest, ruff, mypy, etc.)

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set your `DJANGO_SECRET_KEY` for production.

### 3. Run Migrations

```bash
uv run python manage.py migrate
```

This will create all necessary database tables.

### 4. Verify System

```bash
uv run python manage.py check
```

This verifies that your project is properly configured.

### 5. Create Superuser

```bash
uv run python manage.py createsuperuser
```

Follow the prompts to create an admin user. Alternatively, you can create a superuser non-interactively:

```bash
uv run python manage.py createsuperuser --noinput --username admin --email admin@example.com
```

Then set the password:

```bash
uv run python manage.py changepassword admin
```

### 6. Run Development Server

```bash
uv run python manage.py runserver
```

Or to make it accessible from other devices on your network:

```bash
uv run python manage.py runserver 0.0.0.0:8000
```

Visit `http://127.0.0.1:8000/` to see your Django application.

## Available URLs

Once the server is running, you can access:

### Admin & Portal
- **Admin Panel (Jazzmin)**: http://127.0.0.1:8000/admin/
- **SSO Portal**: http://127.0.0.1:8000/accounts/

### API Documentation
- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc**: http://127.0.0.1:8000/api/schema/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

### API Endpoints
- **JWT Token**: http://127.0.0.1:8000/api/token/
- **SSO Mobile**: http://127.0.0.1:8000/api/sso/authenticate/
- **User Info**: http://127.0.0.1:8000/api/user/
- **Health Check**: http://127.0.0.1:8000/api/health/

## Features

### 🎨 Jazzmin Admin Interface
Modern, responsive admin interface with customizable themes.

### 🔐 SSO Authentication (Portal)
- Google OAuth2
- GitHub OAuth2
- Microsoft OAuth2
- Login/Register via `/accounts/`

### 📱 SSO Authentication (Mobile Apps)
Endpoint for mobile apps to authenticate with SSO tokens:

**POST** `/api/sso/authenticate/`

Request body:
```json
{
  "provider": "google|github|microsoft",
  "access_token": "token_from_provider"
}
```

Response:
```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "is_new_user": false
  }
}
```

**Flow:**
1. Mobile app authenticates with provider (Google/GitHub/Microsoft)
2. Mobile app receives access token from provider
3. Mobile app sends token to `/api/sso/authenticate/`
4. Backend verifies token with provider
5. Backend creates user if new, or finds existing user
6. Backend returns Django JWT tokens for API access

### 🔑 JWT API Authentication
- **POST** `/api/token/` - Get JWT tokens (username/password)
- **POST** `/api/token/refresh/` - Refresh access token
- **POST** `/api/token/verify/` - Verify token validity

Use JWT tokens in API requests:
```
Authorization: Bearer <access_token>
```

### ☁️ Cloud Storage Support
Multiple cloud storage backends for static and media files:
- **AWS S3** - Amazon Web Services
- **Google Cloud Storage** - GCS
- **Azure Blob Storage** - Microsoft Azure
- **DigitalOcean Spaces** - S3-compatible
- **Scaleway Object Storage** - S3-compatible
- **MinIO** - S3-compatible
- **Local Storage** - Default for development

Configure via `STORAGE_BACKEND` environment variable. See `docs/STORAGE_BACKENDS.md` for details.

## Project Structure

```
django-template/
├── config/              # Django project settings
│   ├── settings.py     # Main settings file
│   ├── urls.py         # URL configuration
│   ├── wsgi.py         # WSGI configuration
│   └── asgi.py         # ASGI configuration
├── manage.py           # Django management script
├── pyproject.toml      # Project metadata and dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Development

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run tests with coverage report
uv run pytest --cov=. --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Type check
uv run mypy .
```

### Database Management

```bash
# Create migrations
uv run python manage.py makemigrations

# Apply migrations
uv run python manage.py migrate

# Verify system configuration
uv run python manage.py check

# Access Django shell
uv run python manage.py shell
```

### User Management

```bash
# Create superuser (interactive)
uv run python manage.py createsuperuser

# Create superuser (non-interactive)
uv run python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Change user password
uv run python manage.py changepassword <username>
```

## Configuration

### Environment Variables

The project uses environment variables for configuration. See `.env.example` for available options:

- `DJANGO_SECRET_KEY`: Secret key for cryptographic signing (required in production)
- `DJANGO_DEBUG`: Enable/disable debug mode (default: True)
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DJANGO_LANGUAGE_CODE`: Language code (default: pt-br)
- `DJANGO_TIME_ZONE`: Time zone (default: America/Sao_Paulo)

### Database

By default, the project uses SQLite. To use PostgreSQL or MySQL, update `DATABASES` in `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'mydb'),
        'USER': os.environ.get('DB_USER', 'user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## Testing

The project uses pytest-django for testing. Tests should be placed in:

- `tests/` directory (integration tests)
- `*/tests.py` or `*/test_*.py` files (unit tests)

Coverage threshold: **63%** (current: 64.21%)

## Code Quality Standards

- **Linting**: Ruff (must pass with no warnings)
- **Formatting**: Ruff formatter
- **Type Checking**: mypy (strict mode)
- **Testing**: pytest with 63%+ coverage threshold (current: 64.21%)
- **Python Version**: 3.11+

## License

MIT License

## Contributing

1. Follow the code quality standards
2. Write tests for new features
3. Ensure 63%+ test coverage (threshold configured)
4. Run all quality checks before committing

