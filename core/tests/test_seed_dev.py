import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings


class SeedDevCommandTests(TestCase):
    @override_settings(DEBUG=True)
    def test_seed_creates_and_rotates_password_idempotently(self):
        with patch.dict(os.environ, {'DEV_SEED_ADMIN_PASSWORD': 'StrongDevPass#2026'}):
            call_command('seed_dev', confirm_local=True)
            user = get_user_model().objects.get(email='a@a.com')
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_active)
            self.assertTrue(user.check_password('StrongDevPass#2026'))
            call_command('seed_dev', confirm_local=True)
            self.assertEqual(get_user_model().objects.filter(email='a@a.com').count(), 1)

    @override_settings(DEBUG=False)
    def test_seed_refuses_production(self):
        with (
            patch.dict(os.environ, {'DEV_SEED_ADMIN_PASSWORD': 'StrongDevPass#2026'}),
            self.assertRaises(CommandError),
        ):
            call_command('seed_dev', confirm_local=True)

    @override_settings(DEBUG=True)
    def test_requires_explicit_confirmation_and_password(self):
        with (
            patch.dict(os.environ, {'DEV_SEED_ADMIN_PASSWORD': 'StrongDevPass#2026'}),
            self.assertRaises(CommandError),
        ):
            call_command('seed_dev')
        with patch.dict(os.environ, {'DEV_SEED_ADMIN_PASSWORD': ''}), self.assertRaises(CommandError):
            call_command('seed_dev', confirm_local=True)

    def test_fixture_has_unusable_placeholder_password(self):
        import json
        from pathlib import Path

        path = Path(__file__).resolve().parents[2] / 'fixtures' / 'dev_superuser.json'
        fixture = json.loads(path.read_text(encoding='utf-8'))
        record = fixture[0]
        self.assertEqual(record['fields']['email'], 'a@a.com')
        self.assertTrue(record['fields']['is_staff'])
        self.assertTrue(record['fields']['is_superuser'])
        self.assertFalse(record['fields']['password'].startswith(('pbkdf2_', 'argon2', 'bcrypt')))
        self.assertTrue(record['fields']['password'].startswith('!'))
