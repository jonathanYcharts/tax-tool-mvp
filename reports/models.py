from django.db import models

class GBMTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
    )

    date = models.DateField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    ticker = models.CharField(max_length=10)
    quantity = models.FloatField(null=True, blank=True)
    price_usd = models.FloatField(null=True, blank=True)
    amount_usd = models.FloatField(null=True, blank=True)  # for dividends
    tax_withheld_usd = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.type} {self.ticker}"

class GBMConfirmationTransaction(models.Model):
    symbol = models.CharField(max_length=10)
    security_name = models.CharField(max_length=100, null=True, blank=True)
    action = models.CharField(max_length=10)  # Buy/Sell
    quantity = models.FloatField()
    price = models.FloatField()
    trade_date = models.DateField()
    settle_date = models.DateField()
    capacity = models.CharField(max_length=30)
    commission = models.FloatField(default=0.0)
    transaction_fee = models.FloatField(default=0.0)
    other_fees = models.FloatField(default=0.0)
    net_amount = models.FloatField()
    
    def __str__(self):
        return f"{self.trade_date} - {self.symbol} {self.action} - {self.quantity} @ {self.price}"