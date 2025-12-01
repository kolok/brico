import re

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    """Convert markdown to HTML."""
    if not value:
        return ""

    if isinstance(value, str):
        # Avoid not well displayed code blocks
        value = re.sub(r"\n\s*```", "\n```", value)

    # Configure markdown extensions
    md = markdown.Markdown(extensions=["extra", "nl2br"])

    # Convert markdown to HTML
    html = md.convert(value)
    md.reset()

    return mark_safe(html)
