# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='attr')
def add_attr(field, css):
    attrs = {}
    definition = css.split(',')
    for d in definition:
        if ':' in d:
            key, val = d.split(':')
            attrs[key.strip()] = val.strip()
        else:
            attrs[d.strip()] = True
    return field.as_widget(attrs=attrs)

@register.filter(name='data_attr') # Νέο filter για data attributes
def add_data_attr(field, attrs_string):
    attrs = {}
    pairs = attrs_string.split('|')
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=')
            # Καθαρίζουμε τυχόν εισαγωγικά και spaces
            attrs[key.strip()] = value.strip().strip("'\"") 
        else:
            # Αν δεν υπάρχει =, απλά το προσθέτουμε ως boolean attribute
            attrs[pair.strip()] = True
    return field.as_widget(attrs=attrs)