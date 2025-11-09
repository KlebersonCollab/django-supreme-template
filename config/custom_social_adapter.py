"""Custom Social Account Adapter para garantir que get_app funcione corretamente."""

import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter customizado para garantir que get_app retorne apenas uma app por provider."""

    def list_apps(self, request, provider=None, client_id=None):
        """
        Override list_apps para garantir que retorne apenas uma app por provider.
        
        Se houver múltiplas apps, retorna apenas a primeira e remove as duplicatas.
        
        Args:
            request: HttpRequest object
            provider: Provider name (e.g., 'github', 'google') - optional
            client_id: Client ID (optional, not used)
        
        Returns:
            List with at most one SocialApp instance per provider
        """
        # Se provider não for especificado, chamar método pai
        if provider is None:
            return super().list_apps(request, provider=provider, client_id=client_id)
        
        site = Site.objects.get_current()
        
        # Buscar apps para este provider e site
        apps = list(SocialApp.objects.filter(provider=provider, sites=site))
        
        if len(apps) == 0:
            # Se não encontrar, tentar sem filtro de site
            apps = list(SocialApp.objects.filter(provider=provider))
            if len(apps) > 0:
                # Associar ao site atual
                app = apps[0]
                app.sites.add(site)
                app.save()
                return [app]
            return []
        
        if len(apps) > 1:
            # Se houver múltiplas, manter apenas a primeira e remover as outras
            app = apps[0]
            # Remover duplicatas
            duplicates = SocialApp.objects.filter(provider=provider, sites=site).exclude(pk=app.pk)
            duplicates.delete()
            return [app]
        
        return apps

    def is_open_for_signup(self, request, sociallogin):
        """
        Permite que novos usuários se registrem via OAuth.
        
        Args:
            request: HttpRequest object
            sociallogin: SocialLogin instance
            
        Returns:
            True para permitir signup automático
        """
        return True

    def save_user(self, request, sociallogin, form=None):
        """
        Salva o usuário e adiciona ao grupo "Membro da equipe" por padrão.
        
        Args:
            request: HttpRequest object
            sociallogin: SocialLogin instance
            form: Form instance (optional)
            
        Returns:
            User instance
        """
        # Salvar o usuário usando o método padrão
        user = super().save_user(request, sociallogin, form=form)
        
        # Adicionar ao grupo "Membro da equipe" se existir
        try:
            grupo_membro = Group.objects.get(name="Membro da equipe")
            user.groups.add(grupo_membro)
            logger.info(f"Usuário {user.username} adicionado ao grupo 'Membro da equipe'")
        except Group.DoesNotExist:
            # Se o grupo não existir, criar automaticamente
            grupo_membro = Group.objects.create(name="Membro da equipe")
            user.groups.add(grupo_membro)
            logger.info(f"Grupo 'Membro da equipe' criado e usuário {user.username} adicionado")
        
        return user

    def populate_user(self, request, sociallogin, data):
        """
        Popula dados do usuário a partir dos dados do provider OAuth.
        
        Args:
            request: HttpRequest object
            sociallogin: SocialLogin instance
            data: Dict com dados do provider
        """
        user = sociallogin.user
        
        # Se o email não estiver definido, tentar obter do provider
        if not user.email:
            user.email = data.get("email") or data.get("mail") or ""
        
        # Se o username não estiver definido, gerar a partir do email ou nome
        if not user.username:
            username = (
                data.get("login")  # GitHub
                or data.get("name")  # Google/Microsoft
                or data.get("preferred_username")  # Microsoft
                or (user.email.split("@")[0] if user.email else "user")
            )
            # Garantir que o username seja único
            base_username = username
            counter = 1
            from django.contrib.auth import get_user_model
            User = get_user_model()
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
        
        # Preencher nome e sobrenome se disponível
        if not user.first_name:
            user.first_name = (
                data.get("given_name")  # Google
                or data.get("first_name")  # GitHub
                or ""
            )
        
        if not user.last_name:
            user.last_name = (
                data.get("family_name")  # Google
                or data.get("last_name")  # GitHub
                or ""
            )
        
        return user

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """
        Trata erros de autenticação, incluindo rate limiting do GitHub.
        
        Args:
            request: HttpRequest object
            provider_id: ID do provider (e.g., 'github')
            error: String de erro
            exception: Exception object
            extra_context: Contexto adicional
        """
        # Log do erro para debugging
        logger.error(
            f"Social authentication error for {provider_id}: {error}",
            exc_info=exception,
            extra={"provider": provider_id, "error": error}
        )
        
        # Tratar rate limiting do GitHub especificamente
        if provider_id == "github" and exception:
            error_str = str(exception).lower()
            if "rate limit" in error_str or "too many requests" in error_str or "429" in error_str:
                messages.error(
                    request,
                    "GitHub está limitando requisições. Por favor, aguarde alguns minutos antes de tentar novamente."
                )
                return redirect(reverse("account_login"))
        
        # Para outros erros, usar o comportamento padrão
        return super().authentication_error(request, provider_id, error=error, exception=exception, extra_context=extra_context)

