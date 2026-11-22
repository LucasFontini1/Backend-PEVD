"""Inicialização manual e restrita de uma conta de desenvolvimento."""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = 'Cria/atualiza administrador LOCAL de desenvolvimento, nunca produção.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm-local', action='store_true',
            help='Confirmar explicitamente que este é um banco descartável de DEV.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or not options['confirm_local']:
            raise CommandError('seed_dev exige DEBUG=True e --confirm-local.')
        password = os.environ.get('DEV_SEED_ADMIN_PASSWORD', '')
        if len(password) < 8:
            raise CommandError('Defina DEV_SEED_ADMIN_PASSWORD (ao menos 8 caracteres).')
        User = get_user_model()
        email = 'a@a.com'
        matches = User.objects.select_for_update().filter(email__iexact=email)
        if matches.count() > 1:
            raise CommandError('Foram encontradas contas duplicadas; verifique o banco.')
        user = matches.first()
        if user is None:
            if User.objects.filter(username__iexact='admin.dev').exists():
                raise CommandError('Username admin.dev já pertence a outra conta.')
            user = User.objects.create_superuser(
                email=email, username='admin.dev', password=password,
                name='Administrador de desenvolvimento',
            )
            created = True
        else:
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save(update_fields=['is_staff', 'is_superuser', 'is_active', 'password'])
            created = False
        if not all((user.is_active, user.is_staff, user.is_superuser)):
            raise CommandError('A conta não recebeu todas as permissões esperadas.')
        self.stdout.write(self.style.SUCCESS(
            f"Conta de DEV {'criada' if created else 'atualizada'}: {email} "
            '(is_active/is_staff/is_superuser=True).'
        ))
