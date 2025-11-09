"""Template tags for user avatar display."""

from django import template
from allauth.socialaccount.models import SocialAccount

register = template.Library()


def get_social_avatar_url(user):
    """
    Get avatar URL from social account if available.
    
    Checks SocialAccount extra_data for avatar URLs from different providers:
    - Google: picture
    - GitHub: avatar_url
    - Microsoft: photo or picture
    
    Args:
        user: User instance
        
    Returns:
        Avatar URL string or None
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        # Get the first social account (most recent)
        social_account = SocialAccount.objects.filter(user=user).first()
        if not social_account:
            return None
        
        extra_data = social_account.extra_data or {}
        provider = social_account.provider
        
        # Provider-specific avatar field names
        if provider == "google":
            return extra_data.get("picture")
        elif provider == "github":
            return extra_data.get("avatar_url")
        elif provider == "microsoft":
            return extra_data.get("photo") or extra_data.get("picture")
        
        # Generic fallback
        return (
            extra_data.get("picture")
            or extra_data.get("avatar_url")
            or extra_data.get("photo")
            or extra_data.get("avatar")
        )
    except Exception:
        return None


@register.simple_tag(takes_context=True)
def get_user_avatar_url(context):
    """
    Template tag to get user avatar URL from social account.
    
    Usage in template:
        {% load user_avatar %}
        {% get_user_avatar_url as avatar_url %}
        {% if avatar_url %}
            <img src="{{ avatar_url }}" alt="Avatar" />
        {% endif %}
    """
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return None
    
    return get_social_avatar_url(request.user)


@register.simple_tag
def get_user_avatar(user):
    """
    Template tag expected by Jazzmin to get user avatar URL.
    
    This is the tag that Jazzmin uses in its base template:
    {% get_user_avatar request.user %}
    
    Args:
        user: User instance
        
    Returns:
        Avatar URL string or None
    """
    if not user or not user.is_authenticated:
        return None
    
    return get_social_avatar_url(user)


@register.inclusion_tag("admin/user_avatar.html", takes_context=True)
def user_avatar(context):
    """
    Inclusion tag to render user avatar HTML.
    
    Usage in template:
        {% load user_avatar %}
        {% user_avatar %}
    """
    request = context.get("request")
    avatar_url = None
    
    if request and request.user.is_authenticated:
        avatar_url = get_social_avatar_url(request.user)
    
    return {
        "avatar_url": avatar_url,
        "user": request.user if request else None,
    }

