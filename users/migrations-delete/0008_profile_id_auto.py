# Generated by Django 4.0.4 on 2022-05-30 00:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_profile_cbu'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='id_auto',
            field=models.BooleanField(default=False),
        ),
    ]
