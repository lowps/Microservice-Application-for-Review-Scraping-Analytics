from django.db import models
from django.utils import timezone
import math


class Business(models.Model):
    business_id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.business_name = self.business_name.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.business_name

    class Meta:
        """
        Meta class in a Django model is an inner class used to configure model-level options
        It tells Django how the model should behave. such as its singular/plural names, ordering, database table name, permissions, etc.
        It does not define fields — only metadata about the model.

        Common uses:
        - verbose_name / verbose_name_plural: Human-readable singular and plural names.
        - ordering: Default ordering of model query results.
        - db_table: Custom database table name.
        - unique_together: Multi-field uniqueness constraint.
        - permissions: Custom permissions for the model.

        My use case:
        - verbose_name_plural: Overrides Django's default pluralization (e.g., "Businesss") with "Businesses".

        """

        verbose_name_plural = "Businesses"


class Store(models.Model):
    store_id = models.CharField(max_length=50, unique=True, blank=True)
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        """
        Automatically generates a store_id scoped to the business if one is not manually set.

        - `if not self.store_id:` checks whether store_id is empty, null, or falsy.
        - The custom store_id logic only runs when creating a new Store.
        - It avoids regenerating the ID when updating an existing record.

        On updates:
            - When calling `.save()` on an existing Store, the block is skipped (store_id already exists).
            EX: STARBUCKS-0001 is not regenerated

        On creation:
            - When you create a new Store and dont assign store_id manually:
              `Store.objects.create(business=some_starbucks_business, street="...", ...)`
              → store_id is empty, so the block runs.
              → It finds the latest store for that business (e.g., STARBUCKS-0001)
              → Increments it to generate: STARBUCKS-0002
        """
        if not self.store_id:
            # Get the last store for this business sorted by store_id descending
            last_store = (
                Store.objects.filter(business=self.business)
                .order_by("-store_id")
                .first()
            )
            if last_store:
                try:
                    last_num = int(last_store.store_id.split("-")[-1])
                except (IndexError, ValueError):
                    last_num = 0
            else:
                last_num = 0

            new_num = last_num + 1

            # Normalize business name: remove spaces, uppercase
            business_prefix = self.business.business_name.replace(" ", "").upper()
            self.store_id = f"{business_prefix}-{new_num:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.store_id} - {self.street}, {self.city}, {self.state} {self.zip}"


# Custom Manager: Handles generating/updating parent table & child table with specified data.
class ScrapeEventManager(models.Manager):
    def create_scrape_event(self, data: dict, business_name: str, source: str):
        if not business_name:
            raise Exception("You must provide the business name.")

        business_name = business_name.strip().upper()
        business, _ = Business.objects.update_or_create(business_name=business_name)

        if not source:
            raise Exception(
                "You must provide the source from which you scraped your data."
            )
        source = source.strip().lower()

        # Ensures subcategories exist only once before processing
        subcategories = ["Food", "Service", "Atmosphere"]
        # dictionary comprehension- keys for 'name' are from iterable 'subcategories', keys are Food, Service, Atmosphere
        subcat_objs = {
            name: SubcategoryReview.objects.get_or_create(subcategory_name=name)[0]
            for name in subcategories
        }

        events = []
        subcategory_created = 0
        for entry in data:
            street = entry.get("street")
            city = entry.get("city")
            state = entry.get("state")
            zip = entry.get("zip")

            # Validate
            if not all([street, city, state, zip]):
                raise Exception("Incomplete address information.")

            # Normalize
            street = street.strip().upper()
            city = city.strip().upper()
            state = state.strip().upper()
            zip = zip.strip()

            # Locate existing Store or Create it
            store, _ = Store.objects.update_or_create(
                business=business,
                street=street,
                city=city,
                state=state,
                zip=zip,
            )
            # Creates individual ScrapeEvent records for each Field in child table
            # And scrape_event is linked to parent table store_id
            scrape_event, _ = ScrapeEvent.objects.get_or_create(
                store=store,
                source=source,
            )
            events.append(scrape_event)

            # Customer Review Fields
            date = entry.get("review_date")
            rating = entry.get("review_rating")
            review = entry.get("review_content")
            first_name = entry.get("first_name")
            last_name = entry.get("last_name")

            # Checks if atleast one is missing a value, so returns None
            if not all([date, rating, review, first_name, last_name]):
                return None

            # Create CustomerReview object
            customer_review, _ = CustomerReview.objects.get_or_create(
                scrape_event=scrape_event,
                review_date=date,
                overall_rating=rating,
                review=review,
                first_name=first_name,
                last_name=last_name,
            )

            # Now handle subcategory ratings
            for subcat_name, rating_key in [
                ("Food", "food_rating"),
                ("Service", "service_rating"),
                ("Atmosphere", "atmosphere_rating"),
            ]:
                rating_value = entry.get(rating_key)
                if (
                    rating_value is not None
                    and rating_value != ""
                    and rating_value != "null"
                    and not (
                        isinstance(rating_value, float) and math.isnan(rating_value)
                    )
                ):
                    # .get_or_create(), and this method has a special API. All the fields outside of defaults are used to search for an existing row (get). Any fields not in either part are left blank or get model defaults.
                    # Essentially saying: "Look for a row with this exact review and subcategory. If it exists, return it. If it doesn't exist, create it with the given rating."
                    CustomerSubcategoryReview.objects.get_or_create(
                        review=customer_review,
                        subcategory=subcat_objs[subcat_name],
                        defaults={"rating": rating_value},
                    )
                    subcategory_created += 1

        # Returns the newly created 'ScrapeEvent' Instances
        return events, subcategory_created


class ScrapeEvent(models.Model):
    scrape_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    scrape_date = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=100)

    objects = ScrapeEventManager()

    def save(self, *args, **kwargs):
        """
        custom save is triggered when either one of these occurs:
        1) Manually create a ScrapeEvent
            event = ScrapeEvent(store=some_store, source="GOOGLE MAPS")
            event.save()  # <-- triggers your custom save()
        2) Implicitly, when using Model.objects.create(...)
            ScrapeEvent.objects.create(store=some_store, source="GOOGLE MAPS")
        3) Update cases, when updating existing instances:
            event.source = "Google Maps"
            event.save()  # triggers the custom save
        """
        self.source = self.source.strip().lower()
        super().save(*args, **kwargs)

        def __str__(self):
            return f"ScrapeEvent {self.scrape_id} for {self.store.store_id} on {self.scrape_date.date()}"


class CustomerReview(models.Model):
    review_id = models.AutoField(primary_key=True)
    scrape_event = models.ForeignKey(ScrapeEvent, on_delete=models.CASCADE)
    review_date = models.DateTimeField(default=timezone.now)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    review = models.TextField(db_index=True, null=True, blank=True)
    overall_rating = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Rating: {self.overall_rating} - {self.review[:30]}..."


class CustomerSubcategoryReview(models.Model):
    review = models.ForeignKey(CustomerReview, on_delete=models.CASCADE)
    subcategory = models.ForeignKey("SubcategoryReview", on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ("review", "subcategory")  # Composite Key

    def __str__(self):
        return f"Review {self.review.review_id} - {self.subcategory.subcategory_name}: {self.rating}"


class SubcategoryReview(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    subcategory_name = models.CharField(
        max_length=100, null=True, blank=True, unique=True
    )

    def __str__(self):
        return self.subcategory_name or "No Subcategory Review"
