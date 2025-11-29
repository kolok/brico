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

    # Normalize escape characters if necessary
    # Convert \' sequences to single quotes
    if isinstance(value, str):
        # Replace common JSON escape sequences
        value = value.replace("\\'", "'")
        value = value.replace("\\n", "\n")
        value = value.replace("\\t", "\t")
        value = re.sub(r"\n\s*```", "\n```", value)

    # Configure markdown extensions
    # "extra" already includes fenced_code and tables, so we use it as base
    extensions = [
        "extra",  # Additional extensions (includes fenced_code, tables, etc.)
        "nl2br",  # Automatic line breaks
    ]

    # Create markdown instance with extensions
    md = markdown.Markdown(extensions=extensions)

    # Convert markdown to HTML
    html = md.convert(value)

    # Reset instance to avoid cache issues
    md.reset()

    return mark_safe(html)
