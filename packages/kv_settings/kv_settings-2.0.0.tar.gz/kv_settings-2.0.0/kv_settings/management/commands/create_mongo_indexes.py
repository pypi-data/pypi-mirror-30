from django.core.management import BaseCommand
from django.conf import settings

import pymongo


class Command(BaseCommand):
    help = 'Removes (if exists) and creates all the required Mongo DB indeces'

    # A command must define handle()
    def handle(self, *args, **options):
        self.stdout.write('Dropping all indexes...')
        settings.DB.customers.drop_indexes()
        settings.DB.orders.drop_indexes()
        settings.DB.products.drop_indexes()
        settings.DB.checkouts.drop_indexes()
        self.stdout.write('All indexes dropped...')

        self.stdout.write('Creating indexes for customers...')
        settings.DB.customers.create_index(
            [('id', pymongo.ASCENDING), ('store.id', pymongo.ASCENDING)],
            unique=True)
        self.stdout.write('Created...')

        self.stdout.write('Creating indexes for orders...')
        settings.DB.orders.create_index(
            [('id', pymongo.ASCENDING), ('store.id', pymongo.ASCENDING)],
            unique=True)
        self.stdout.write('Created...')

        self.stdout.write('Creating indexes for products...')
        settings.DB.products.create_index(
            [('id', pymongo.ASCENDING), ('store.id', pymongo.ASCENDING)],
            unique=True)
        self.stdout.write('Created...')

        self.stdout.write('Creating indexes for checkouts...')
        settings.DB.checkouts.create_index(
            [('id', pymongo.ASCENDING), ('store.id', pymongo.ASCENDING)],
            unique=True)
        self.stdout.write('Created...')
