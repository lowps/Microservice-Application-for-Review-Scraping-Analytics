# Register your models here.
from django.contrib import admin
from django.utils import dateformat
from django.utils.html import format_html
from django.conf import settings
from .models import (
    Business,
    Store,
    ScrapeEvent,
    CustomerReview,
    CustomerSubcategoryReview,
    SubcategoryReview,
)
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import SimpleListFilter
import re


class StoreFilter(SimpleListFilter):
    title = "store"
    parameter_name = "scrape_event__store"

    def lookups(self, request, model_admin):
        from .models import Store

        store_list = []
        for store in Store.objects.all():
            # Extract everything up to the second hyphen using regex
            match = re.match(r"([A-Z]+-\d{4})", str(store))
            label = match.group(1) if match else str(store)
            store_list.append((store.id, label))

        return store_list

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(scrape_event__store__id=value)
        return queryset


class StoreSubcatFilter(SimpleListFilter):
    title = "store"
    parameter_name = "scrape_event__store"

    def lookups(self, request, model_admin):
        store_list = []
        for store in Store.objects.all():
            # extract just “STARBUCKS-0001” from the __str__:
            match = re.match(r"([A-Z]+-\d{4})", str(store))
            label = match.group(1) if match else str(store)
            store_list.append((store.id, label))

        return store_list

    def queryset(self, request, queryset):
        """
        Djangos ORM, the double-underscore (__) syntax lets you traverse different models and access their properties/attributes via the ForeignKey & dunder.
            -> review: "review" refers to the ForeignKey field on the CustomerSubcategoryReview model. Follow its ForeignKey to the CustomerReview instance/table/model, enabling access to its properties
            -> scrape_event: On that CustomerReview, follow its scrape_event ForeignKey to the ScrapeEvent instance.
            -> store: On that ScrapeEvent, follow its store ForeignKey to the Store instance.
            -> id: Finally, access the id field (primary key) of that Store.
            EX: review__scrape_event__store__id=value

        """
        value = self.value()
        if value:
            return queryset.filter(review__scrape_event__store__id=value)
        return queryset


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("business_id", "business_name")  # columns shown in list view
    search_fields = ("business_name",)  # Adds searchbar


@admin.register(CustomerReview)
class CustomerReviewAdmin(admin.ModelAdmin):
    list_per_page = 50
    list_display = (
        "get_formatted_date",
        "first_name",
        "last_name",
        "review",
        "overall_rating",
    )

    list_filter = (
        StoreFilter,
        "overall_rating",
        ("review_date", admin.DateFieldListFilter),
    )

    search_fields = (
        "first_name",
        "last_name",
        "review",
    )

    ordering = ("-review_date",)  # Default ordering: most recent first

    def get_formatted_date(self, obj):
        return dateformat.format(obj.review_date, "F j, Y")

    get_formatted_date.short_description = "Review Date"  # Column header
    get_formatted_date.admin_order_field = "review_date"  # Allows sorting by date


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "store_id",
        "store_id_link",
        "store_to_subcat_reviews",
        "business",
        "street",
        "city",
        "state",
        "zip",
    )
    list_filter = ("business", "city", "state")
    raw_id_fields = ("business",)

    def store_id_link(self, obj):
        # Filters CustomerReview via scrape_event__store__id
        url = reverse("admin:starbuck_customerreview_changelist") + f"?store={obj.pk}"
        return format_html('<a href="{}">View Reviews</a>', url)

    def store_to_subcat_reviews(self, obj):
        # Must point at CustomerSubcategoryReview changelist
        url = (
            reverse("admin:starbuck_customersubcategoryreview_changelist")
            + f"?store={obj.pk}"
        )
        return format_html('<a href="{}">Subcat Reviews</a>', url)

    store_to_subcat_reviews.short_description = "Access Subcategory Reviews"
    store_id_link.short_description = "Access Reviews"
    store_id_link.admin_order_field = "store_id"


class CustomerReviewInline(admin.TabularInline):
    """
    Django Admin inlines are designed to edit child models from their parent's admin page.
    The ForeignKey relationship: CustomerReview has a ForeignKey to ScrapeEvent, thus to view your
    CustomerReviewInline changes in Django Admin, you need to register it with the parent model's ModelAdmin


    Note- The model chain is: Business → Store → ScrapeEvent → CustomerReview → ...

    """

    model = CustomerReview
    can_delete = False
    extra = 0  # prevents empty inline forms
    fields = (
        "review_id",
        "review_date",
        "first_name",
        "last_name",
        "review",
        "overall_rating",
    )


@admin.register(ScrapeEvent)
class ScrapeEventAdmin(admin.ModelAdmin):
    inlines = [CustomerReviewInline]
    list_display = ("scrape_id", "store", "source", "scrape_date")
    date_hierarchy = "scrape_date"


@admin.register(CustomerSubcategoryReview)
class CustomerSubcategoryReviewAdmin(admin.ModelAdmin):
    list_display = (
        "get_formatted_date",
        "get_customer_name",
        "get_subcategory_name",
        "rating",
    )
    list_filter = (
        StoreSubcatFilter,
        "subcategory",
        "rating",
        ("review__review_date", admin.DateFieldListFilter),
    )
    search_fields = (
        "review__first_name",
        "review__last_name",
        "subcategory__subcategory_name",
    )

    ordering = ("-review__review_date",)  # Descending order default

    def get_review_id(self, obj):
        return obj.review.review_id

    def get_formatted_date(self, obj):
        return dateformat.format(obj.review.review_date, "F j, Y")

    def get_customer_name(self, obj):
        return f"{obj.review.first_name} {obj.review.last_name}"

    def get_subcategory_name(self, obj):
        return obj.subcategory.subcategory_name

    get_review_id.short_description = "Review ID"
    get_formatted_date.short_description = "Review Date"
    get_formatted_date.admin_order_field = "review__review_date"
    get_customer_name.short_description = "Customer"
    get_subcategory_name.short_description = "Subcategory"
