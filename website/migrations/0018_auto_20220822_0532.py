# Generated by Django 2.2.28 on 2022-08-22 05:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_remove_lists_game_skips_per_player'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lists_game',
            name='words',
        ),
        migrations.AddField(
            model_name='word',
            name='lists_game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.lists_game'),
        ),
        migrations.AlterField(
            model_name='lists_game',
            name='host',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='host', to=settings.AUTH_USER_MODEL),
        ),
    ]