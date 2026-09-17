# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class BillingHistory(models.Model):
    user = models.ForeignKey('Users', models.DO_NOTHING)
    plan = models.ForeignKey('SubscriptionPlans', models.DO_NOTHING)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    transaction_id = models.CharField()
    invoice_path = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'billing_history'


class Comments(models.Model):
    post = models.ForeignKey('Posts', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    text = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'


class Likes(models.Model):
    post = models.ForeignKey('Posts', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'likes'


class Posts(models.Model):
    title = models.CharField()
    content = models.TextField()
    author = models.ForeignKey('Users', models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    image = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'posts'


class SubscriptionPlans(models.Model):
    name = models.CharField()
    price = models.TextField()  # This field type is a guess.
    max_posts = models.IntegerField(blank=True, null=True)
    max_images_per_post = models.IntegerField(blank=True, null=True)
    max_likes = models.IntegerField(blank=True, null=True)
    max_comments = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subscription_plans'


class Users(models.Model):
    username = models.CharField()
    email = models.CharField()
    password = models.CharField()
    subscription_plan_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
