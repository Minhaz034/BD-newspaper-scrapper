# Generated by Django 2.1.15 on 2023-02-16 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraping', '0002_auto_20230216_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='link',
            field=models.CharField(default='', max_length=2083),
        ),
    ]
