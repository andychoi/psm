# Generated by Django 4.0.4 on 2022-05-23 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_alter_milestone_finish_alter_milestone_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='milestone',
            name='finish',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
