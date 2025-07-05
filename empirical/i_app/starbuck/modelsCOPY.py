from django.db import models
from django.utils import timezone

# Create your models here.
from django.db import models
import random
import string

# Create your models here.


def generate_random_store_id(
    length: int = 4,
):  # Possibly use this for generating codes associated w/ food items
    """Generate a random alphanumeric string of the specified length"""
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


def generate_sequential_store_id():
    """
    Generatea sequential store ID based on the most recent store ID.
    Example: Generates IDs like STORE-0001, STORE-0002, etc.
    """
    last_store = Starbucks.objects.order_by("-store_id").first()
    last_id = int(last_store.store_id.split("-")[1]) if last_store else 0
    new_id = last_id + 1
    return f"STORE-{new_id:04d}"


# Parent Table
class Starbucks(models.Model):
    id = models.AutoField(primary_key=True)
    store_id = models.CharField(
        max_length=50, unique=True, default=generate_sequential_store_id
    )
    date_scraped = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"Store ID: {self.store_id}"


# Custom Manager: Handles generating/updating parent table & child table with specified data.
class ProductScrapeEventManager(models.Manager):
    def create_scrape_event(self, data: dict, address: str):
        # Check if the address list is valid (must contain exactly one address)
        if not address:
            raise Exception("You must provide an address for the store.")

        address_value = address  # Extracts the single address from the list

        # Verifies if Starbucks parent table is created then creates it or if already created then updates it.
        # Adds input address to the parent table field/attribute/column
        starbucks, _ = Starbucks.objects.update_or_create(address=address_value)

        events = []
        # data is a list of dictionaries
        for entry in data:
            review = entry.get("review_content")
            rating = entry.get("review_rating")
            author = entry.get("review_author")
            date = entry.get("review_date")
            category = entry.get("category_ratings")

            # Checks if atleast one is missing a value, so returns None
            if not all([review, rating, author, date, category]):
                return None

            # Creates individual ProductScrapeEvent records for each Field in child table
            # And starbucks is linked to parent table store_id
            event = self.create(
                starbucks=starbucks,
                date=date,
                author=author,
                review=review,
                rating=rating,
                category=category,
            )
            events.append(event)

        # Returns the newly created 'ProductScrapeEvent' Instances
        return events or None


# child table
class ProductScrapeEvent(models.Model):
    # ForeignKey link to parent table. Cascading Behavior: When the parent object is deleted, all related child objects are automatically deleted too.
    starbucks = models.ForeignKey(Starbucks, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    author = models.CharField(max_length=100, null=True, blank=True)
    review = models.TextField(db_index=True, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    category = models.TextField(null=True, blank=True)

    # This line assigns the ‘ProductScrapeEventManager’ instance to ‘objects’ within ProductScrapeEvent (model); allowing usage of ‘create_scrape_event() and other manager methods
    objects = ProductScrapeEventManager()

    # String Representation Method- Allows you to view the 'ProductScrapeEvent' instance/object in Django Admin or shell, displaying a summary of each review record.
    # view a django object from django datatype to a more user friendly representation via __str__
    def __str__(self):
        return f"Review for StoreID: {self.starbucks.store_id} ({self.starbucks.address}): {self.review[:30]}... RATING:{self.rating}"
