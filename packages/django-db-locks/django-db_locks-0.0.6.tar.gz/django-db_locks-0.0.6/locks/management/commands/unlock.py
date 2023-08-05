from django.core.management.base import BaseCommand, CommandError
from locks.locks import DbLock
from locks.models import Lock


class Command(BaseCommand):
    help = 'start/stop a TxBroadcaster'

    def add_arguments(self, parser):
        parser.add_argument('name', nargs=1, type=str)

    def handle(self, *args, **options):
        self.stdout.write('Unlocking all locks')
        if options['name'] == 'all':
            for i in Lock.objects.all():
                i.locked = False
                i.save()
                self.stdout.write('Unlocked {}'.format(i.name))
            return

        self.stdout.write('unlocking: {name}'.format(
            name=options['name'][0]))
        DbLock(name=options['name'][0]).release(hard=True)
        self.stdout.write('unlocked!')



