from django.core.management.base import BaseCommand

from ...models import Replay


class Command(BaseCommand):
    help = "Re-process all replays."

    def handle(self, *args, **options):
        print args, options

        replays = Replay.objects.all()

        for replay in replays:
            if replay.replay_id and replay.file:
                print 'Processing', replay.replay_id
                replay.processed = False
                replay.save()