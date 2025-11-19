from django.core.management.base import BaseCommand
from django_seed import Seed
from chats.models import Conversation, Message
from django.contrib.auth import get_user_model
from django.db import transaction
from random import randint, choice, sample
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = "Seed the database with sample Users, Conversations, and Messages."

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create.')
        parser.add_argument('--conversations', type=int, default=15, help='Number of conversations to create.')
        parser.add_argument('--messages', type=int, default=5, help='Number of messages per conversation.')

    def handle(self, *args, **options):
        seeder = Seed.seeder()
        num_users = options['users']
        num_conversations = options['conversations']
        num_messages_per_conv = options['messages']

        self.stdout.write(self.style.WARNING("Starting database seeding..."))

        users = []
        for i in range(num_users):
            email = seeder.faker.unique.email()
            
            users.append(User.objects.create_user(
                email=email,
                password='password123', 
                username=email,
                first_name=seeder.faker.first_name(),
                last_name=seeder.faker.last_name(),
                role=choice(['guest', 'host', 'admin']),
                phone_number=seeder.faker.phone_number(),
            ))
        if len(users) < 2:
            self.stdout.write(self.style.ERROR("Need at least 2 users to create conversations."))
            return

        conversations = []
        for _ in range(num_conversations):
            conv = Conversation.objects.create()
            participants = sample(users, k=randint(2, min(5, len(users))))
            conv.participants.set(participants)
            conversations.append(conv)

        self.stdout.write(self.style.SUCCESS(f"Created {len(conversations)} conversations with unique participants."))

        message_data = []
        for conv in conversations:
            participants = list(conv.participants.all())
            last_sent_time = timezone.now() - timedelta(days=randint(1, 30))
            for _ in range(num_messages_per_conv):
                sender = choice(participants)
                minutes_gap = randint(1, 120)
                last_sent_time += timedelta(minutes=minutes_gap)

                message_data.append(Message(
                    conversation=conv,
                    sender=sender,
                    message_body=seeder.faker.text(max_nb_chars=150),
                    sent_at=last_sent_time
                ))

        with transaction.atomic():
            Message.objects.bulk_create(message_data)

        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(message_data)} messages with realistic chronological order."))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
