# Generated by Django 4.2.4 on 2023-08-05 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teams',
            name='team_member',
        ),
        migrations.AddField(
            model_name='teams',
            name='team_member',
            field=models.ManyToManyField(related_name='member_teams', to='home.students'),
        ),
    ]