# Generated by Django 4.2.4 on 2023-09-21 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_events_rules'),
    ]

    operations = [
        migrations.AlterField(
            model_name='events',
            name='category',
            field=models.CharField(choices=[('Technical', 'Technical'), ('Non-Technical', 'Non-Technical'), ('Cultural', 'Cultural')], default='O', max_length=30),
        ),
    ]