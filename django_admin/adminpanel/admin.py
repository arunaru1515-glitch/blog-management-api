from django.contrib import admin
from .models import Posts, SubscriptionPlans, Users, BillingHistory


@admin.register(Posts)
class PostsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author_id",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
    )

    list_filter = (
        "created_at",
    )


@admin.register(SubscriptionPlans)
class SubscriptionPlansAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "max_posts",
        "max_images_per_post",
        "max_likes",
        "max_comments",
    )

    search_fields = (
        "name",
    )


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "subscription_plan_id",
    )

    search_fields = (
        "username",
        "email",
    )

    list_filter = (
        "subscription_plan_id",
    )


@admin.register(BillingHistory)
class BillingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_id",
        "plan_id",
        "start_date",
        "end_date",
        "transaction_id",
        "invoice_path",
    )

    search_fields = (
        "transaction_id",
    )

    list_filter = (
        "start_date",
        "end_date",
    )