# Generated by Django 4.1 on 2022-08-31 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0002_post_liked_by'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Comment',
        ),
    ]
