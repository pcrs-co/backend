from django.core.management.base import BaseCommand
from ai_recommender.extractor.extractor import run_extraction_for_all_apps
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Extract system requirements for applications missing them."

    def handle(self, *args, **options):
        self.stdout.write("Starting extraction of system requirements...")
        try:
            run_extraction_for_all_apps()
            self.stdout.write(self.style.SUCCESS("Extraction completed successfully!"))
        except Exception as e:
            logger.exception("Extraction failed.")
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
