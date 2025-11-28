import re

import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    """Convertit du markdown en HTML."""
    if not value:
        return ""

    # Normaliser les caractères d'échappement si nécessaire
    # Convertir les séquences \' en apostrophes simples
    if isinstance(value, str):
        # Remplacer les séquences d'échappement JSON courantes
        value = value.replace("\\'", "'")
        value = value.replace("\\n", "\n")
        value = value.replace("\\t", "\t")
        value = re.sub(r"\n\s*```", "\n```", value)
    print(value)
    # Configuration des extensions markdown
    # "extra" inclut déjà fenced_code et tables, donc on l'utilise comme base
    extensions = [
        "extra",  # Extensions supplémentaires (inclut fenced_code, tables, etc.)
        "nl2br",  # Retours à la ligne automatiques
    ]

    # Créer l'instance markdown avec les extensions
    md = markdown.Markdown(extensions=extensions)

    # Convertir le markdown en HTML
    html = md.convert(value)

    # Réinitialiser l'instance pour éviter les problèmes de cache
    md.reset()

    return mark_safe(html)
