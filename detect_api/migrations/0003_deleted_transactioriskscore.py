# Generated by Django 5.0.7 on 2024-08-06 14:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('detect_api', '0002_rename_transaction_transactioriskscore_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TransactioRiskScore',
        ),
    ]
