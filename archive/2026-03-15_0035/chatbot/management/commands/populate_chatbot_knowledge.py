"""
Management command to populate chatbot knowledge base
"""
from django.core.management.base import BaseCommand
from apps.chatbot.models import ChatbotKnowledge
from apps.chatbot.seed_data import CHATBOT_KNOWLEDGE


class Command(BaseCommand):
    help = 'Populate chatbot knowledge base with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading chatbot knowledge base...')
        
        created_count = 0
        updated_count = 0
        
        for item in CHATBOT_KNOWLEDGE:
            knowledge, created = ChatbotKnowledge.objects.update_or_create(
                question=item['question'],
                defaults={
                    'category': item['category'],
                    'answer': item['answer'],
                    'keywords': item['keywords'],
                    'priority': item['priority'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {item["question"][:50]}...')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {item["question"][:50]}...')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully loaded {created_count} new and updated {updated_count} existing knowledge entries'
            )
        )
