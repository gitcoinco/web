from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--network',
            '-n',
            dest='network',
            help='The network the match contract has been deployed (eg. mainnet, rinkeby)',
            required=True,

        )

    def handle(self, *args, **kwargs):
        pass
