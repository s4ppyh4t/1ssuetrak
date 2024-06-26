from django import template
from django.utils.safestring import mark_safe
import re

register: template.Library = template.Library()

@register.filter(name='highlight')
def highlight(text, search_term):
  if not search_term:
    return text
  
  # highlighted = re.compile(re.escape(search_term), re.IGNORECASE)
  return mark_safe(re.sub('(?i)(%s)' % (re.escape(search_term)),'<span class="text-warning">\\1</span>', text))
