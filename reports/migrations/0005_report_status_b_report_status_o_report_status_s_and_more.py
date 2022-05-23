# Generated by Django 4.0.4 on 2022-05-22 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_alter_report_status_milestone'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='status_b',
            field=models.CharField(choices=[('10-green', 'Green'), ('20-yellow', 'Yellow'), ('20-red', 'Red'), ('00-completed', 'Completed')], default='10-green', max_length=20, verbose_name='status budget'),
        ),
        migrations.AddField(
            model_name='report',
            name='status_o',
            field=models.CharField(choices=[('10-green', 'Green'), ('20-yellow', 'Yellow'), ('20-red', 'Red'), ('00-completed', 'Completed')], default='10-green', max_length=20, verbose_name='status overall'),
        ),
        migrations.AddField(
            model_name='report',
            name='status_s',
            field=models.CharField(choices=[('10-green', 'Green'), ('20-yellow', 'Yellow'), ('20-red', 'Red'), ('00-completed', 'Completed')], default='10-green', max_length=20, verbose_name='status scope'),
        ),
        migrations.AddField(
            model_name='report',
            name='status_t',
            field=models.CharField(choices=[('10-green', 'Green'), ('20-yellow', 'Yellow'), ('20-red', 'Red'), ('00-completed', 'Completed')], default='10-green', max_length=20, verbose_name='status schedule'),
        ),
        migrations.AlterField(
            model_name='milestone',
            name='status',
            field=models.CharField(choices=[('10-green', 'Green'), ('20-yellow', 'Yellow'), ('20-red', 'Red'), ('00-completed', 'Completed')], default='10-green', max_length=20, verbose_name='status overall'),
        ),
        migrations.AlterField(
            model_name='report',
            name='status',
            field=models.IntegerField(choices=[(0, 'Draft'), (1, 'Publish'), (2, 'Delete')], default=0),
        ),
    ]
