"""Custom Account Adapter para adicionar usuários ao grupo padrão."""

import logging
from allauth.account.adapter import DefaultAccountAdapter
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)


class CustomAccountAdapter(DefaultAccountAdapter):
    """Adapter customizado para adicionar novos usuários ao grupo 'Membro da equipe'."""

    def save_user(self, request, user, form, commit=True):
        """
        Salva o usuário e adiciona ao grupo "Membro da equipe" por padrão.
        
        Args:
            request: HttpRequest object
            user: User instance
            form: Form instance
            commit: Whether to commit the user to database
            
        Returns:
            User instance
        """
        # Salvar o usuário usando o método padrão
        user = super().save_user(request, user, form, commit=commit)
        
        # Se commit=True, adicionar ao grupo
        if commit:
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

