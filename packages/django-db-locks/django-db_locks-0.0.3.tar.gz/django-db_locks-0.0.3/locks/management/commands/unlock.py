from django.core.management.base import BaseCommand, CommandError
from locks.locks import DbLock


class Command(BaseCommand):
    help = 'start/stop a TxBroadcaster'

    def add_arguments(self, parser):
        parser.add_argument('uid', nargs=1, type=int)

    def handle(self, *args, **options):
        self.stdout.write('unlocking: {uid}'.format(
            uid=options['uid'][0]))
        DbLock(name=options['uid'][0]).release(hard=True)
        self.stdout.write('unlocked!')



