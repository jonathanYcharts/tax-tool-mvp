# Generated by Django 5.2.1 on 2025-05-27 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="GBMConfirmationTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("symbol", models.CharField(max_length=10)),
                (
                    "security_name",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("action", models.CharField(max_length=10)),
                ("quantity", models.FloatField()),
                ("price", models.FloatField()),
                ("trade_date", models.DateField()),
                ("settle_date", models.DateField()),
                ("capacity", models.CharField(max_length=30)),
                ("commission", models.FloatField(default=0.0)),
                ("transaction_fee", models.FloatField(default=0.0)),
                ("other_fees", models.FloatField(default=0.0)),
                ("net_amount", models.FloatField()),
            ],
        ),
    ]
