# Generated by Django 3.0.4 on 2020-03-11 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exlibris', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='books', to='exlibris.Author'),
            preserve_default=False,
        ),
    ]
