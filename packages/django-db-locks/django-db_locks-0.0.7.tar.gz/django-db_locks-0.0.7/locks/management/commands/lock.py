from django.core.management.base import BaseCommand, CommandError
from locks.locks import DbLock


class Command(BaseCommand):
    help = 'lock a db lock'

    def add_arguments(self, parser):
        parser.add_argument('uid', nargs=1, type=int)

    def handle(self, *args, **options):
        self.stdout.write('locking: {uid}'.format(
            uid=options['uid'][0]))
        DbLock(name=options['uid'][0]).set(hard=True)
        self.stdout.write('locked!')


