# Generated by Django 2.1.7 on 2019-03-10 15:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0022_auto_20190310_0622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='server',
            name='moderation_message',
            field=models.TextField(blank=True, default='', help_text='Message that will be shown to user if server is rejected.'),
        ),
    ]
