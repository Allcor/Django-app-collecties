from django.core.management.base import BaseCommand

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('session_key', type=str)

    def _key_to_user(self, session_key):
        session = Session.objects.get(session_key=session_key)
        session_data = session.get_decoded()
        uid = session_data.get('_auth_user_id')
        user = User.objects.get(id=uid)
        return user.username

    def handle(self, *args, **options):
        username = self._key_to_user(options['session_key'])
        self.stdout.write(username)