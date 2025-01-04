
from django import template
register = template.Library()
import ast

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else None



@register.filter
def add_commas(value):
    try:
        return "{:,.2f}".format(float(value)) 
    except (ValueError, TypeError):
        return value 




@register.filter
def in_list(value, arg):
    if not isinstance(arg, list):
        return False
    return value in arg



@register.filter
def item_list(value, arg):
    return value in arg.split(',')




@register.filter
def in_list2(value, arg):
    if isinstance(arg, str):
        try:
            arg = ast.literal_eval(arg)  
        except (ValueError, SyntaxError):
            return False
    return value in arg




@register.filter(name='add_class')
def add_class(value, css_class):
    return value.as_widget(attrs={'class': css_class})



@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def has_pending_extension_requests(task):
    return task.time_extension_requests.filter(is_approved=False).exists()



