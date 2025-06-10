from django.core.management.base import BaseCommand
from ai_recommender.scraper import run_extraction_for_all_activities


class Command(BaseCommand):
    help = "Extract applications for all activities"

    def handle(self, *args, **kwargs):
        run_extraction_for_all_activities()
        self.stdout.write(self.style.SUCCESS("Extraction complete!"))
