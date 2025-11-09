"""Template tags customizados para providers sociais."""

from django import template
from allauth.socialaccount.templatetags.socialaccount import get_providers as allauth_get_providers
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

register = template.Library()

# Mapeamento de providers para classes CSS do Jazzmin
PROVIDER_BUTTON_CLASSES = {
    "google": "danger",
    "github": "dark",
    "microsoft": "info",
    "facebook": "primary",
    "twitter": "info",
    "linkedin": "primary",
    "apple": "dark",
}

# Mapeamento de providers para ícones FontAwesome
PROVIDER_ICONS = {
    "google": "fab fa-google",
    "github": "fab fa-github",
    "microsoft": "fab fa-microsoft",
    "facebook": "fab fa-facebook",
    "twitter": "fab fa-twitter",
    "linkedin": "fab fa-linkedin",
    "apple": "fab fa-apple",
}


@register.simple_tag(takes_context=True)
def get_unique_providers(context):
    """
    Retorna uma lista de providers sociais únicos que têm SocialApp configurada.
    
    Filtra apenas providers que realmente têm uma SocialApp associada ao site atual,
    evitando erros DoesNotExist quando o template tenta gerar URLs.
    
    Args:
        context: Template context
        
    Returns:
        Lista de providers únicos com SocialApp configurada
    """
    try:
        providers = allauth_get_providers(context)
    except Exception:
        # Se houver erro ao buscar providers, retornar lista vazia
        return []
    
    # Obter site atual
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        return []
    
    # Obter IDs de providers que têm SocialApp configurada
    configured_provider_ids = set(
        SocialApp.objects.filter(sites=site).values_list("provider", flat=True).distinct()
    )
    
    # Filtrar apenas providers configurados e remover duplicatas
    seen = set()
    unique_providers = []
    
    for provider in providers:
        if provider.id in configured_provider_ids and provider.id not in seen:
            seen.add(provider.id)
            unique_providers.append(provider)
    
    return unique_providers


@register.simple_tag
def get_provider_button_class(provider_id):
    """
    Retorna a classe CSS do botão para um provider específico.
    
    Args:
        provider_id: ID do provider (e.g., 'google', 'github')
        
    Returns:
        Classe CSS do botão (e.g., 'danger', 'dark', 'info')
    """
    return PROVIDER_BUTTON_CLASSES.get(provider_id, "primary")


@register.simple_tag
def get_provider_icon(provider_id):
    """
    Retorna o ícone FontAwesome para um provider específico.
    
    Args:
        provider_id: ID do provider (e.g., 'google', 'github')
        
    Returns:
        Classe do ícone FontAwesome (e.g., 'fab fa-google')
    """
    return PROVIDER_ICONS.get(provider_id, "fas fa-sign-in-alt")

