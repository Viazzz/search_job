# Generated by Django 5.1.7 on 2025-04-07 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hh_search', '0009_alter_foundvacancies_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foundvacancies',
            name='snippet_requirement',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='foundvacancies',
            name='snippet_responsibility',
            field=models.TextField(blank=True, null=True),
        ),
    ]
