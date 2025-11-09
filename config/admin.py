"""Custom Django Admin configuration."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from allauth.socialaccount.models import SocialAccount

User = get_user_model()


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


# Unregister the default UserAdmin if already registered
if admin.site.is_registered(User):
    admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User Admin with social avatar support."""
    
    def get_avatar_html(self, obj):
        """Generate HTML for user avatar."""
        avatar_url = get_social_avatar_url(obj)
        
        if avatar_url:
            return format_html(
                '<img src="{}" alt="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #ddd;" />',
                avatar_url,
                obj.username or "User"
            )
        # Fallback: show first letter of username
        initial = obj.username[0].upper() if obj.username else "?"
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background-color: #007bff; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px;">{}</div>',
            initial
        )
    
    get_avatar_html.short_description = "Avatar"
    
    # Add avatar to list display
    list_display = ("get_avatar_html", "username", "email", "first_name", "last_name", "is_staff", "is_active", "date_joined")
    list_display_links = ("get_avatar_html", "username")
    
    # Add avatar to user detail page
    readonly_fields = ("get_avatar_html",)
    
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Avatar", {
            "fields": ("get_avatar_html",),
            "description": "Avatar from social account (Google, GitHub, Microsoft)"
        }),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("username", "email", "password1", "password2")}),
    )

