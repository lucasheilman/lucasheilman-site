# Generated by Django 2.0.2 on 2018-03-02 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='social_media',
            name='link',
            field=models.TextField(default='link'),
            preserve_default=False,
        ),
    ]
