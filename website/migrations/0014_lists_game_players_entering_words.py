# Generated by Django 2.2.28 on 2022-08-09 05:02

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0013_auto_20220809_0442'),
    ]

    operations = [
        migrations.AddField(
            model_name='lists_game',
            name='players_entering_words',
            field=models.ManyToManyField(blank=True, related_name='players_entering_words', to=settings.AUTH_USER_MODEL),
        ),
    ]
