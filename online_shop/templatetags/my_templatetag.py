from django import template
from django.contrib.auth.models import Group


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group =  Group.objects.get_or_create(name=group_name)
    return True if group[0] in user.groups.all() else False


@register.filter(name='markdown_to_html')
def markdown_to_html(text):
    while '\n' in text:
        text = text.replace('\n', '<br>')
    return text

