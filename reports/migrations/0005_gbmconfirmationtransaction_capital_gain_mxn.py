# Generated by Django 5.2.1 on 2025-06-03 04:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0004_gbmconfirmationtransaction_mxn_amount"),
    ]

    operations = [
        migrations.AddField(
            model_name="gbmconfirmationtransaction",
            name="capital_gain_mxn",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
