# Register your models here.
from django.contrib import admin
from .models import Starbucks, ProductScrapeEvent
from django.utils.html import format_html
from django.conf import settings

# Register your models here so it appears in the DJANGO Admin Interface


# Inline admin for displaying ProductScrapeEvent entries within Starbucks
# In the Django admin interface, when you click on a model like Starbucks and
# then select a specific instance (e.g., STORE-0002), you can see related records
# from another model that references Starbucks through a ForeignKey (ex: ProductScrapeEvent).
# This behavior is enabled by the inlines configuration in the admin, as demonstrated with
# TabularInline or StackedInline.
class ProductScrapeEventInline(admin.TabularInline):
    model = ProductScrapeEvent
    extra = 0  # No extra blank rows for adding reviews by deafault
    can_delete = False
    fields = (
        "date",
        "author",
        "review",
        "rating_stars",
        "category",
    )  # Use actual field names here
    readonly_fields = (
        "review_preview",
        "rating_stars",
    )  # custom methods here

    def review_preview(self, obj):
        return obj.review[:50] + "..." if obj.review else "-"

    review_preview.short_description = "Review Preview"

    def rating_stars(self, obj):
        return "★" * obj.rating if obj.rating else "-"

    rating_stars.short_description = "Rating"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("starbucks")  # Optimize queries


# Admin for Starbucks with inline reviews
@admin.register(Starbucks)
class StarbucksAdmin(admin.ModelAdmin):
    list_display = ["store_id", "date_scraped", "address", "review_count"]
    search_fields = ["store_id", "address"]
    inlines = [ProductScrapeEventInline]

    def review_count(self, obj):
        return obj.productscrapeevent_set.count()

    review_count.short_description = "Reviews"


# Admin for ProductScrapeEvent (option: if needed for detailed review management)
# Create a custom Admin of 'ProductScrapeEvent'
@admin.register(ProductScrapeEvent)
class ProductScrapeEventAdmin(admin.ModelAdmin):
    # list_display NORMALIZES entries by: replacing underscores with spaces, title casing all to UPPER
    list_display = (
        "starbucks",
        "get_address",
        "formatted_date",
        "author",
        "rating",
        "review",
        "category",
    )
    search_fields = (
        "starbucks__store_id",
        "starbucks__address",
        "review",
        "author",
        "date",
    )
    list_select_related = ("starbucks",)  # For better performance
    list_per_page = 50
    fieldsets = (
        ("Store Information", {"fields": ("starbucks",)}),
        ("Review Details", {"fields": ("date", "author", "rating")}),
        ("Review Content", {"fields": ("review", "category")}),
    )

    # Custom method to display the address from the related Starbucks model
    # self: refers to admin instance 'ProductScrapeEventAdmin
    # obj: is the 'ProductScrapeEvent' Model instance being displayed or interacted with in Django admin interface
    # obj.starbucks: accessing the foreign key 'starbucks' to access the linked model/table 'starbucks'
    # obj.starbucks.address: accessing the field/attribute 'address' via foreign key (since foreign key is linked to parent table)
    def get_address(self, obj):
        return (
            obj.starbucks.address
        )  # Accesses the address field through the ForeignKey

    get_address.short_description = "Address"  # Label for the column in the admin panel
    get_address.admin_order_field = "starbucks__address"

    def rating_stars(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            "gold" if obj.rating >= 4 else "black",
            "★" * obj.rating,
        )

    rating_stars.short_description = "Rating"

    def review_preview(self, obj):
        return obj.review[:75] + "..." if obj.review else "-"

    review_preview.short_description = "Review Preview"

    def formatted_date(self, obj):
        return obj.date.strftime("%b %d, %Y") if obj.date else ""

    formatted_date.short_description = "Date"
    formatted_date.admin_order_field = "date"
