

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else None



@register.filter
def add_commas(value):
    try:
        return "{:,.2f}".format(float(value)) 
    except (ValueError, TypeError):
        return value 
