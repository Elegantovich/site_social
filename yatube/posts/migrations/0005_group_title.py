# Generated by Django 2.2.19 on 2021-08-21 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_auto_20210821_1737'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='title',
            field=models.CharField(default='default title', max_length=200),
        ),
    ]
