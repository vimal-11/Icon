# Generated by Django 4.2.4 on 2023-08-07 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_students_id_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField()),
                ('currency', models.CharField(max_length=3)),
                ('status', models.CharField(max_length=20)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.events')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.students')),
            ],
        ),
    ]
