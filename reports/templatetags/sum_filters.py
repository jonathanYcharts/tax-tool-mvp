from django import template

register = template.Library()

@register.filter
def sum_mxn(queryset):
    return round(sum(tx.mxn_amount or 0 for tx in queryset), 2)

@register.filter
def sum_gain(transactions):
    return round(sum(tx.capital_gain_mxn or 0 for tx in transactions), 2)
