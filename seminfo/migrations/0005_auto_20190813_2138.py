# Generated by Django 2.2.2 on 2019-08-13 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seminfo', '0004_auto_20190811_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='lec_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subjectmonth',
            name='lec_total',
            field=models.IntegerField(default=0),
        ),
    ]
