# Generated by Django 4.2.4 on 2023-09-13 07:55

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_payment_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='events',
            name='rules',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
    ]