# Generated by Django 3.0.4 on 2020-05-05 09:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exlibris', '0006_auto_20200505_0257'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='rank',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
