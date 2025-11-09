"""Views customizadas para o Django Admin."""

from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme


def admin_login_redirect(request):
    """
    Redireciona /admin/login/ para /accounts/login/.
    
    Isso unifica a experiência de login usando o Allauth,
    que tem mais funcionalidades (signup, email login, OAuth).
    
    Preserva o parâmetro ?next= para redirecionar após login.
    
    IMPORTANTE: Se o usuário já estiver autenticado, redireciona direto para /admin/
    para evitar loops de redirecionamento.
    """
    # Se já estiver autenticado, vai direto para o admin
    if request.user.is_authenticated:
        next_url = request.GET.get("next", "/admin/")
        return redirect(next_url)
    
    # Se não estiver autenticado, redireciona para login do Allauth
    next_url = request.GET.get("next", "/admin/")
    # Validar que a URL é segura antes de passar como parâmetro
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return redirect(f"{reverse('account_login')}?next={next_url}")
    return redirect(f"{reverse('account_login')}?next=/admin/")

