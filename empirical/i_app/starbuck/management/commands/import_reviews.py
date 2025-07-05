import os
from pathlib import Path
import sys
import django
import pandas as pd
from django.db import transaction
from django.core.management.base import BaseCommand
from django.utils import timezone
import pytz

# goes to i_app
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(BASE_DIR))

# from b_utils.logger import Logger
# from b_utils.helper import get_directory_name

# absolute_path = "django_gun/empirical/i_app/starbuck/management/commands"
# inspector_gadget = get_directory_name(absolute_path)
# inspector_gadget = Logger(inspector_gadget)


class Command(BaseCommand):
    """
    Django management command to import Starbucks reviews from a processed CSV file.

    This command:
    - Takes a file path as input (containing review data)
    - Processes and validates each review record
    - Imports the data into the database via ScrapeEvent model
    - Provides detailed success/failure reporting

    Example usage:
        python manage.py import_reviews /path/to/file.csv \
            --business_name "STARBUCKS" \
            --source "GOOGLE_MAPS"

    File format expected:
        review_date, review_rating, review_content, first_name, last_name, street, city, state, zip, category_ratings
    """

    help = "Import Starbucks reviews from processed CSV file."

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        # Set up Django environment:
        sys.path.insert(
            0,
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ),
        )
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings.local")
        django.setup()
        from starbuck.models import ScrapeEvent

        self.ScrapeEvent = ScrapeEvent

    def add_arguments(self, parser):
        """
        Custom code via inheritance that allows me to specify the path
        to a file (file_path), file_path is the argument to the cli command.
        The method parses the CSV file.

        Note: Parser object is instantiated by parent class and the parent class
        calls upon the child class method signature self.add_arguments(parser), the
        parser object is the argument input. Parent class has a method with the
        method signature "add_arguments(self, parser)" and its default does nothing because
        it is a hook for child classes to use with custom management commands
        (to define command line arguments)

        """
        parser.add_argument(
            "file_path",
            type=str,
            help="Path to the processed CSV file",
        )
        parser.add_argument(
            "--business_name",
            type=str,
            required=True,
            help="Name of the business (ex: 'STARBUCKS')",
        )
        parser.add_argument(
            "--source",
            type=str,
            required=True,
            help="Source of the scraped data (ex: 'GOOGLE MAPS)",
        )

    def handle(self, *args, **options):
        # Load and prepare the DataFrame
        try:
            df = pd.read_csv(options["file_path"])
            df.sort_values(by="review_date", ascending=False, inplace=True)
            self.import_data(
                df,
                business_name=options["business_name"],
                source=options["source"],
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Verify if business_name, source are provided & file_path is correct: {str(e)}"
                )
            )

    def import_data(self, df, business_name, source):
        total_rows = len(df)
        success_count = 0
        subcategory_count = 0

        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Convert naive datetime to timezone-aware
                    naive_date = pd.to_datetime(row.get("review_date"))
                    aware_date = timezone.make_aware(
                        naive_date, timezone.get_current_timezone()
                    )
                    # Prepare review data
                    review_data = {
                        "review_date": aware_date,
                        "review_rating": row.get("review_rating"),
                        "review_content": row.get("review_content"),
                        "first_name": row.get("first_name"),
                        "last_name": row.get("last_name"),
                        # address
                        "street": str(row.get("street", "")).strip(),
                        "city": str(row.get("city", "")).strip(),
                        "state": str(row.get("state", "")).strip(),
                        "zip": str(row.get("zip", "")).strip(),
                        # subcategory
                        "food_rating": row.get("food_rating"),
                        "service_rating": row.get("service_rating"),
                        "atmosphere_rating": row.get("atmosphere_rating"),
                    }

                    # Validate required fields
                    # strip whitespace to avoid blank spaces being counted as valid
                    required_fields = [
                        review_data["street"],
                        review_data["city"],
                        review_data["state"],
                        review_data["zip"],
                    ]
                    if not all(required_fields):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping row {index}: MISSING REQUIRED FIELDS"
                            )
                        )
                        continue

                    # Create the records
                    result, subcat_num = self.ScrapeEvent.objects.create_scrape_event(
                        data=[review_data],
                        business_name=business_name,
                        source=source,
                    )

                    if result:
                        success_count += 1
                        subcategory_count += subcat_num

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping row {index}: {str(e)}")
                    )
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported {success_count}/{total_rows} reviews AND {subcategory_count} subcategory reviews"
            )
        )
