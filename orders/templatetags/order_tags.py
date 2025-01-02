# orders/templatetags/order_tags.py

from django import template

register = template.Library()

@register.filter
def split_customer_info(note):
    """Extract customer info from order note"""
    info = {'name': '', 'phone': '', 'notes': ''}
    if note:
        lines = note.split('\n')
        for line in lines:
            if 'Nama:' in line:
                info['name'] = line.replace('Nama:', '').strip()
            elif 'Telepon:' in line:
                info['phone'] = line.replace('Telepon:', '').strip()
            elif 'Catatan:' in line:
                info['notes'] = line.replace('Catatan:', '').strip()
    return info

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value"""
    return value - arg