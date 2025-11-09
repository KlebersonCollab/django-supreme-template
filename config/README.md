# Config Package Structure

This directory contains the Django project configuration and core modules.

## Core Files (Required)

### Django Configuration (Auto-loaded)
- **`settings.py`** - Main Django settings file (auto-loaded via `DJANGO_SETTINGS_MODULE`)
- **`urls.py`** - URL routing configuration (auto-loaded via `ROOT_URLCONF` in settings)
- **`asgi.py`** - ASGI configuration for async Django (auto-loaded by ASGI server)
- **`wsgi.py`** - WSGI configuration for production (auto-loaded by Gunicorn/WSGI server)
- **`__init__.py`** - Makes `config` a Python package (auto-loaded when package is imported)

### API & Views (Auto-loaded via URLs)
- **`api_v1.py`** - API version 1 URL patterns (auto-loaded via `urls.py`)
- **`api_views.py`** - API view functions (auto-loaded via `urls.py` and `api_v1.py`)
- **`exceptions.py`** - Custom exception handlers (auto-loaded via `settings.py` → `REST_FRAMEWORK.EXCEPTION_HANDLER`)

### Authentication & Security (Auto-loaded via Settings)
- **`sso_auth.py`** - SSO authentication for mobile apps (auto-loaded via `urls.py` and `api_v1.py`)
- **`custom_social_adapter.py`** - Custom Django Allauth adapter for social login (auto-loaded via `settings.py` → `SOCIALACCOUNT_ADAPTER`)
- **`custom_account_adapter.py`** - Custom Django Allauth adapter for account signup (auto-loaded via `settings.py` → `ACCOUNT_ADAPTER`)
- **`secrets.py`** - Secrets management (AWS, GCP, Azure, Vault) (auto-loaded via `settings.py` import)

### Admin & Views (Auto-loaded via URLs)
- **`admin_views.py`** - Custom admin views (auto-loaded via `urls.py`)
- **`admin.py`** - Custom Django Admin configuration with social avatar support (auto-loaded by Django admin autodiscovery)

### Template Tags (Auto-loaded by Django)
- **`templatetags/`** - Custom Django template tags (auto-loaded when templates are rendered)
  - **`social_providers.py`** - Template tag for unique social providers

### Utilities (Manual Execution)
- **`setup_social_apps.py`** - Script to setup social OAuth apps from environment variables
  - **Execution**: Manual via `make setup-social-apps` or `python manage.py shell -c "exec(open('config/setup_social_apps.py').read())"`
  - **Purpose**: One-time setup or when OAuth credentials change

## Auto-Loading vs Manual Execution

### ✅ Auto-Loaded (No Manual Invocation Needed)

These files are automatically loaded by Django or referenced by other auto-loaded files:

1. **`settings.py`** - Loaded automatically when Django starts (via `DJANGO_SETTINGS_MODULE`)
2. **`urls.py`** - Loaded automatically by Django (via `ROOT_URLCONF` in settings)
3. **`asgi.py`** - Loaded automatically by ASGI servers (e.g., Uvicorn)
4. **`wsgi.py`** - Loaded automatically by WSGI servers (e.g., Gunicorn)
5. **`exceptions.py`** - Loaded automatically when DRF processes exceptions (via `REST_FRAMEWORK.EXCEPTION_HANDLER`)
6. **`secrets.py`** - Loaded automatically when `settings.py` imports it
7. **`custom_account_adapter.py`** - Loaded automatically by Allauth when processing account signup (via `ACCOUNT_ADAPTER`)
8. **`custom_social_adapter.py`** - Loaded automatically by Allauth when processing social login (via `SOCIALACCOUNT_ADAPTER`)
9. **`admin_views.py`** - Loaded automatically when `urls.py` imports it
10. **`admin.py`** - Loaded automatically by Django admin autodiscovery
11. **`api_views.py`** - Loaded automatically when `urls.py` and `api_v1.py` import it
12. **`sso_auth.py`** - Loaded automatically when `urls.py` and `api_v1.py` import it
13. **`api_v1.py`** - Loaded automatically when `urls.py` includes it
14. **`templatetags/`** - Loaded automatically by Django when templates use `{% load %}` tags

### ⚙️ Manual Execution Required

Only one file requires manual execution:

1. **`setup_social_apps.py`** - Must be executed manually:
   - Via Makefile: `make setup-social-apps`
   - Via Django shell: `python manage.py shell -c "exec(open('config/setup_social_apps.py').read())"`
   - **When**: After setting up OAuth credentials in `.env` or when credentials change
   - **Purpose**: Creates `SocialApp` instances in the database from environment variables

## File Dependencies

All files (except `setup_social_apps.py`) are part of the automatic Django loading chain:

```
Django Startup
  ↓
settings.py (DJANGO_SETTINGS_MODULE)
  ├─→ secrets.py (imported)
  ├─→ exceptions.py (REST_FRAMEWORK.EXCEPTION_HANDLER)
  ├─→ custom_account_adapter.py (ACCOUNT_ADAPTER)
  └─→ custom_social_adapter.py (SOCIALACCOUNT_ADAPTER)
  ↓
urls.py (ROOT_URLCONF)
  ├─→ admin_views.py (imported)
  ├─→ api_views.py (imported)
  ├─→ sso_auth.py (imported)
  └─→ api_v1.py (included)
      ├─→ api_views.py (imported)
      └─→ sso_auth.py (imported)
  ↓
Django Admin (autodiscovery)
  └─→ admin.py (auto-loaded by admin autodiscovery)
  ↓
Templates (when rendered)
  └─→ templatetags/ (auto-loaded via {% load %})
```

## Notes

- **99% of files are auto-loaded**: Only `setup_social_apps.py` requires manual execution
- **No manual imports needed**: All other files are automatically discovered and loaded by Django
- **Production-ready**: All auto-loaded files are production-ready and require no manual intervention
- **One-time setup**: `setup_social_apps.py` is typically run once after deployment or when OAuth credentials change
