# Generated by Django 4.2.4 on 2023-08-16 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='year',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
