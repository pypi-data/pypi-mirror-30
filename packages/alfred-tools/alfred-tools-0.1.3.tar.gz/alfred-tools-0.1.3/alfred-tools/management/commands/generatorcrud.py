from django.core.management.base import BaseCommand, CommandError
 

class Command(BaseCommand):
    help = 'Hi this is one lala'

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='+', type=str)

    def handle(self, *args, **options):
        print (" modelo actualidado")