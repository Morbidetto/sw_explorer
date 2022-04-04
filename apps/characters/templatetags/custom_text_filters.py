

from django import template

register = template.Library()

@register.filter
def cut_from_count_columns(value: str, arg: str) -> str:
    return value.replace(f"{arg},", "")