from django.db import models


# Create your models here.
class News(models.Model):
    newspaper = models.CharField(max_length=30, default="", blank=True, null=True)
    link = models.CharField(max_length=2083, default="")
    language = models.CharField(max_length=20)
    date = models.DateTimeField()
    section = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    headline = models.CharField(max_length=200)
    description = models.CharField(max_length=20000, default="")
    sentiment = models.CharField(max_length=20)

# class News(models.Model):
#
#     title = models.CharField(max_length=200)
#     link = models.CharField(max_length=2083, default="", unique=True)
#     published = models.DateTimeField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     source = models.CharField(max_length=30, default="", blank=True, null=True)
