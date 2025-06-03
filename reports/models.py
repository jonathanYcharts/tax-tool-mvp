from django.db import models
from datetime import date


class GBMConfirmationTransaction(models.Model):
    symbol = models.CharField(max_length=10)
    security_name = models.CharField(max_length=255)
    action = models.CharField(max_length=10)
    execution_time = models.CharField(max_length=20, default='')
    quantity = models.FloatField()
    price = models.FloatField()
    trade_date = models.DateField()
    settle_date = models.DateField()
    capacity = models.CharField(max_length=50)
    commission = models.FloatField()
    transaction_fee = models.FloatField()
    other_fees = models.FloatField()
    net_amount = models.FloatField()
    upload_date = models.DateField(auto_now_add=True)
    mxn_amount = models.FloatField(null=True, blank=True)
    # Only for "Sell" action instances
    capital_gain_mxn = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} {self.action} {self.quantity} @ {self.price}"


class ExchangeRate(models.Model):
    date = models.DateField(unique=True)
    rate = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)
