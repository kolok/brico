from typing import Any

from django import template

register = template.Library()


@register.inclusion_tag("components/tiles.html", takes_context=True)
def tiles(
    context: Any,
    items: list,
    tile_template: str,
    empty_message: str = "",
    add_url: str = "",
    add_label: str = "",
    add_description: str = "",
) -> dict[str, Any]:
    """Render a tiles list from an object list.

    Args:
        context: The template context (automatically passed).
        items: The list of objects to display as tiles.
        tile_template: Path to the template used to render each tile.
        empty_message: Message shown when the list is empty.
        add_url: Optional resolved URL for the "add new" tile.
        add_label: Optional label for the "add new" tile.
        add_description: Optional description for the "add new" tile.
    """
    # Flatten the parent context so sub-templates can access
    # variables like project, audit, request, etc.
    flat: dict[str, Any] = context.flatten()
    flat.update(
        {
            "items": items,
            "tile_template": tile_template,
            "empty_message": empty_message,
            "add_url": add_url,
            "add_label": add_label,
            "add_description": add_description,
        }
    )
    return flat
