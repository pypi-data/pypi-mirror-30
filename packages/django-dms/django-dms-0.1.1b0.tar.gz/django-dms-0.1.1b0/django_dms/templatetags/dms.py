import math
import numbers

from django import template

register = template.Library()

@register.filter
def longitude(value):
    if not isinstance(value, numbers.Number):
        return value
    if value > 180 or value < -180:
        return value
    if value > 0:
        side = 'E'
    elif value < 0:
        side = 'W'
    else:
        side = ''
    return get_degree(value, side)

@register.filter
def latitude(value):
    if not isinstance(value, numbers.Number):
        return value
    if value > 90 or value < -90:
        return value
    if value > 0:
        side = 'N'
    elif value < 0:
        side = 'S'
    else:
        side = ''
    return get_degree(value, side)

def get_degree(value, side):
    result = u'{d}\u00b0 {m}\' {s}" {side}'
    abs_value = math.fabs(value)
    degrees = math.trunc(abs_value)
    minutes = math.trunc((abs_value * 60) % 60)
    seconds = round((abs_value * 3600) % 60)
    if seconds >= 60:
        seconds = 0
        minutes += 1
    minutes = str(minutes).zfill(2)
    seconds = str(seconds).zfill(2)
    return result.format(side=side, d=degrees, m=minutes, s=seconds)

