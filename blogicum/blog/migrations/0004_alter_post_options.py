# Generated by Django 3.2.16 on 2025-02-26 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20250226_2030'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'публикация', 'verbose_name_plural': 'Публикации'},
        ),
    ]
