# Templates - Webapp Agent Notes (Django + Hotwire)

This document describes the conventions and practices for Django templates in the webapp application.

## Overview

- **Template engine**: Django Templates
- **Frontend framework**: Hotwire (Turbo Frames + Stimulus)
- **Styling**: Tailwind CSS
- **Internationalization**: Django i18n (`{% load i18n %}`)
- **Location**: `templates/` directory

## Template Structure

### Directory Organization

Templates are organized by Django app, following the app structure:

```
templates/
├── layout/              # Base templates
│   ├── base.html        # Base template for public pages
│   ├── base-logged.html # Base template for authenticated pages
│   └── center_base.html # Centered layout variant
├── components/          # Reusable components (shared across apps)
│   └── messages.html    # Django messages component
├── audits/              # Templates for audits app
│   ├── comment/         # Comment-related templates
│   │   ├── form.html
│   │   ├── list.html
│   │   └── …
│   ├── project/         # Project-related templates
│   │   ├── list.html
│   │   ├── detail.html
│   │   └── …
│   ├── prompt/          # Prompt-related templates
│   │   ├── detail.html
│   │   └── form.html
│   ├── resource/        # Resource-related templates
│   │   ├── detail.html
│   │   ├── new.html
│   │   └── …
│   └── …                # Other subdirectories (projectaudit/, projectauditcriterion/, etc.)
├── account/             # Django-allauth templates
│   ├── login.html
│   ├── signup.html
│   └── …
└── socialaccount/       # Social auth templates
    ├── login.html
    └── …
```

### Naming Conventions

- **Template files**: for each django app, and by object typology <app>/<object>/<template.html>, e.g., `audits/project/list.html`, `audits/comment/form.html`
- **Component files**: placed in `components/` subdirectory, e.g., `components/message.html`
- **Layout files**: placed in `layout/` directory, prefixed with `base-`, e.g., `base.html`, `base-logged.html`

## Template Inheritance

### Base Templates

- `layout/base.html` : Base template for public/unauthenticated pages
- `layout/base-logged.html` : Base template for authenticated pages (extends `base.html`)

### Extending Templates

Always extend the appropriate base template:

```django
{% extends 'layout/base-logged.html' %}
{% load i18n %}

{% block title %}{% translate "My Projects - Cosqua" %}{% endblock %}

{% block content %}
    <!-- Page content -->
{% endblock content %}
```

## Turbo Frames

### Overview

Turbo Frames enable partial page updates without full page reloads. They are the primary mechanism for dynamic interactions.

### Basic Usage

#### Creating a Turbo Frame

```django
<turbo-frame id="comments_frame">
    <!-- Frame content -->
</turbo-frame>
```

### Frame Naming Conventions

- Use descriptive, unique IDs: `comments_frame`, `comment_form_frame`, `prompts_frame`
- For item-specific frames, include the ID: `comment_{{ comment.id }}`
- Use snake_case for frame IDs

### Best Practices for Turbo Frames

1. **Always wrap frame content**: Every response that updates a frame should wrap content in the matching `<turbo-frame>` tag
2. **Use unique IDs**: Frame IDs must be unique on the page
3. **Target explicitly**: Always specify `data-turbo-frame` when targeting frames
4. **Handle empty states**: Provide empty frame templates for initial states
5. **Keep frames focused**: Each frame should handle one logical piece of functionality

## Components

### Reusable Components

Components are reusable template fragments placed in `components/` directories.

- `templates/{app}/components/`: App-Specific component
- `templates/components/`: Shared Components

### Including Components

Use `{% include %}` to include components:

```django
{% include "components/messages.html" %}
```

### Component Best Practices

1. **Keep components small**: Focus on a single responsibility
2. **Pass context explicitly**: Use `with` to pass variables to components
3. **Document dependencies**: Comment what variables/components are needed
4. **Reuse when appropriate**: Extract common patterns into components

## Internationalization (i18n)

### Loading i18n

Always load i18n at the top of templates that contain user-facing text:

```django
{% load i18n %}
```

### Translating Strings

#### Simple Translation

```django
{% translate "Hello" %}
```

#### Translation with Context

```django
{% translate "Hello" context "greeting" %}
```

#### Block Translation (for pluralization)

```django
{% blocktranslate count count=project.audits.count|default:0 %}
    {{ count }} Audit
{% plural %}
    {{ count }} Audits
{% endblocktranslate %}
```

#### Translation in Attributes

```django
<input placeholder="{% translate 'Search by project name…' %}">
```

### Best Practices for i18n

1. **Always translate user-facing strings**: All text visible to users should be translatable
2. **Use blocktranslate for variables**: When strings contain variables, use `blocktranslate`
3. **Extract messages**: Run `make makemessages` after adding new translatable strings
4. **Update translations**: Edit `locale/fr/LC_MESSAGES/django.po` and run `make compilemessages`

## Styling and CSS Management

### Design System Architecture

The styling approach follows a clear separation of concerns:

1. **Design System**: All reusable design patterns are defined in `static/to_compile/css/base.css`
2. **Color Palette**: All colors are managed in `tailwind.config.js`
3. **Specific Adaptations**: Only use Tailwind utility classes directly in HTML for page-specific or one-off styling needs

### Design System (`base.css`)

The design system in `base.css` contains all reusable components and patterns:

- **Layout components**: `header`, `main`, `footer`, `.main-layout`, `.content`
- **UI components**: `.btn`, `.btn-primary`, `.btn-secondary`, `.card`
- **Form elements**: `input`, `label`, `.helptext`
- **Typography**: `h1`, `h2`, `h3`, `a`
- **App-specific components**: `.tile`, `.tiles`, `.tile-even`, `.tile-odd`
- **Interactive components**: `.tooltip-group`, `.tooltip-block`, `.tooltip-block-bottom` (tooltips), `.kpi-bar`, `.kpi-bar-item` (KPI bars)

**Example from `base.css`:**

```css
.btn-primary {
  @apply bg-primary text-primary_text border-border hover:bg-primary_hover hover:text-primary_hover_text transition;
}

.tile {
  @apply block p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow no-underline text-content;
}
```

### Color Management (`tailwind.config.js`)

All colors are centralized in `tailwind.config.js`:

```javascript
theme: {
  colors: {
    bg_layout: "#96B9D4",      // header, left panel, footer
    bg_content: "#EDF5FB",     // main content
    primary: "#2563eb",
    primary_hover: "#1d4ed8",
    primary_text: "white",
    // … more colors
  },
}
```

**Rules for colors:**

- ✅ Define all colors in `tailwind.config.js`
- ✅ Use semantic color names (e.g., `primary`, `bg_content`, `nav_link`)
- ✅ Reference colors from config in `base.css` using Tailwind syntax
- ❌ Don't hardcode hex colors in templates or CSS

### Using the Design System

#### Preferred: Design System Classes

Always prefer design system classes from `base.css`:

```django
<!-- Use design system classes -->
<button class="btn btn-primary">{% translate "Submit" %}</button>
<a href="…" class="btn btn-secondary">{% translate "Cancel" %}</a>

<!-- Use design system components -->
<div class="card">
    <!-- Card content -->
</div>

<!-- Use design system layout -->
<main class="content">
    <div class="tiles">
        <a href="…" class="tile tile-even">
            <!-- Tile content -->
        </a>
    </div>
</main>
```

#### Allowed: Tailwind Utilities for Specific Adaptations

Use Tailwind utility classes directly only for:

- **Page-specific layouts**: spacing, flexbox arrangements unique to one page
- **One-off styling**: adjustments that don't belong in the design system
- **Responsive adaptations**: breakpoint-specific adjustments

```django
<!-- ✅ Good: Specific layout for this page -->
<form method="get" class="mb-6">
    <div class="flex gap-2">
        <input type="text" name="search" class="flex-1">
        <button type="submit" class="btn btn-primary">{% translate "Search" %}</button>
    </div>
</form>

<!-- ✅ Good: One-off spacing adjustment -->
<div class="mt-6 space-y-4">
    <!-- Content -->
</div>

<!-- ❌ Bad: Should be in design system if reused -->
<div class="bg-white border border-gray-200 rounded-lg p-4">
    <!-- This pattern should be extracted to base.css as .card or similar -->
</div>
```

### Common Patterns

#### Buttons

```django
<!-- Primary button (from design system) -->
<button class="btn btn-primary">{% translate "Submit" %}</button>

<!-- Secondary button (from design system) -->
<a href="…" class="btn btn-secondary">{% translate "Cancel" %}</a>
```

#### Forms

```django
<!-- Form uses design system input/label styles -->
<form method="post">
    {% csrf_token %}
    <!-- Specific layout with Tailwind utilities -->
    <div class="flex gap-2 mb-4">
        <input type="text" name="search" class="flex-1">
        <button type="submit" class="btn btn-primary">{% translate "Search" %}</button>
    </div>
</form>
```

#### Cards and Tiles

```django
<!-- Use design system card class -->
<div class="card">
    <!-- Card content -->
</div>

<!-- Use design system project tiles -->
<div class="tiles">
    <a href="…" class="tile tile-even">
        <h2>Project Name</h2>
    </a>
</div>
```

#### Tooltips

The tooltip component provides hover-based information displays. It uses Tailwind's `group` class mechanism for hover state management.

**Architecture:**

The tooltip component uses a three-layer structure:

1. **`.tooltip-group`**: The container element that must also include Tailwind's `group` class. This element serves as the hover trigger and positioning context.
2. **`.tooltip-block`**: The actual tooltip content container, positioned absolutely above the trigger element. It remains hidden by default and becomes visible on `group-hover`.
3. **`.tooltip-block-bottom`**: An optional decorative element (arrow/triangle) positioned at the bottom of the tooltip block, pointing to the trigger element.

**Important:** The `.tooltip-group` element **must** include the Tailwind `group` class alongside it for the hover mechanism to work. This is because the `.tooltip-block` uses `group-hover:opacity-100` and `group-hover:visible` to control visibility.

**Usage:**

```django
<div class="tooltip-group group">
    <!-- Trigger element (e.g., KPI bar, icon, text) -->
    <div class="kpi-bar">
        <!-- Content that triggers tooltip on hover -->
    </div>

    <!-- Tooltip content (hidden by default, shown on hover) -->
    <span class="tooltip-block">
        <!-- Tooltip content (e.g., legend items) -->
        <span class="kpi-legend-line">
            <span class="kpi-legend-dot bg-green"></span>
            <span class="kpi-legend-text">{% translate "Compliant" %}</span>
        </span>
        <!-- Optional: decorative arrow pointing down -->
        <span class="tooltip-block-bottom"></span>
    </span>
</div>
```

**Key points:**

- ✅ Always use `tooltip-group group` (both classes) on the container element
- ✅ The `.tooltip-block` is absolutely positioned and appears above the trigger element
- ✅ The `.tooltip-block-bottom` element creates a visual arrow connecting the tooltip to the trigger
- ✅ The tooltip automatically shows/hides on hover thanks to Tailwind's `group-hover` mechanism
- ✅ The component is defined in `static/to_compile/css/tooltip.css`

**Example from the codebase:**

```django
<div class="tooltip-group group">
    <div class="kpi-bar">
        <div class="kpi-bar-item bg-green" style="width: 75%"></div>
        <div class="kpi-bar-item bg-orange" style="width: 15%"></div>
    </div>
    <span class="tooltip-block">
        <span class="kpi-legend-line">
            <span class="kpi-legend-dot bg-green"></span>
            <span class="kpi-legend-text">75% {% translate "Compliant" %}</span>
        </span>
        <span class="tooltip-block-bottom"></span>
    </span>
</div>
```

### Best Practices for Styling

1. **Design system first**: Always check if a pattern exists in `base.css` before creating new styles
2. **Extract reusable patterns**: If you use the same Tailwind combination 3+ times, add it to `base.css`
3. **Colors in config**: Never hardcode colors; always reference from `tailwind.config.js`
4. **Semantic color names**: Use semantic names (`primary`, `bg_content`) not generic ones (`blue-600`)
5. **Specific adaptations only**: Use Tailwind utilities directly only for page-specific needs
6. **Keep base.css organized**: Group related styles together (buttons, forms, layout, etc.)

### When to Add to Design System

Add a pattern to `base.css` when:

- ✅ It's used in 3+ different places
- ✅ It represents a reusable UI component (buttons, cards, forms)
- ✅ It's part of the core design language

Keep in Tailwind utilities when:

- ✅ It's specific to one page or template
- ✅ It's a one-off layout adjustment
- ✅ It's a temporary or experimental style

## Forms

### Django Forms

#### Rendering Forms

```django
<form method="post" action="{% url 'audits:comment_create' project.slug audit.id criterion.id %}">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">{% translate "Submit" %}</button>
</form>
```

#### Custom Form Rendering

```django
<form method="post">
    {% csrf_token %}
    <div class="space-y-4">
        <div>
            <label for="{{ form.name.id_for_label }}">{% translate "Name" %}</label>
            {{ form.name }}
            {% if form.name.errors %}
                <div class="text-red-600">{{ form.name.errors }}</div>
            {% endif %}
        </div>
        <!-- More fields -->
    </div>
    <button type="submit">{% translate "Submit" %}</button>
</form>
```

### Form Best Practices

1. **Always include CSRF token**: Use `{% csrf_token %}` in all forms
2. **Handle errors**: Display form errors appropriately
3. **Use proper HTTP methods**: POST for mutations, GET for searches
4. **Target Turbo Frames**: Use `data-turbo-frame` for form submissions if needed
5. **Form rendering**: prefer "Rendering Form" than "Custom Form Rendering"

## Template Tags and Filters

### Custom Template Tags

Custom template tags are located in `{app}/templatetags/`:

```python
# audits/templatetags/markdown_filters.py
from django import template
import markdown

register = template.Library()

@register.filter
def markdownify(text):
    return markdown.markdown(text)
```

Usage:

```django
{% load markdown_filters %}
{{ content|markdownify }}
```

### Common Built-in Filters

- `|date:"d/m/Y H:i"` - Format dates
- `|truncatewords:5` - Truncate text
- `|title` - Title case
- `|default:0` - Default value

## Best Practices Summary

### Structure

1. ✅ Extend appropriate base template (`base.html` or `base-logged.html`)
2. ✅ Organize templates by app in `templates/{app}/`
3. ✅ Place reusable components in `components/` subdirectories
4. ✅ Use descriptive, lowercase file names with underscores

### Turbo Frames

1. ✅ Wrap all frame content in matching `<turbo-frame>` tags
2. ✅ Use unique, descriptive frame IDs
3. ✅ Always specify `data-turbo-frame` when targeting frames
4. ✅ Provide empty frame templates for initial states

### Internationalization

1. ✅ Load `{% load i18n %}` in all templates with user-facing text
2. ✅ Translate all user-visible strings
3. ✅ Use `blocktranslate` for strings with variables
4. ✅ Extract and compile messages after adding translations

### CSS and Styling

1. ✅ Use design system classes from `base.css` for reusable patterns
2. ✅ Define all colors in `tailwind.config.js` with semantic names
3. ✅ Use Tailwind utilities directly only for page-specific adaptations
4. ✅ Extract patterns to `base.css` if used 3+ times
5. ✅ Never hardcode colors; always reference from `tailwind.config.js`
6. ✅ Prefer semantic color names (`primary`, `bg_content`) over generic ones

### Code Quality

1. ✅ Keep templates small and focused
2. ✅ Extract repeated patterns into components
3. ✅ Use semantic HTML
4. ✅ Maintain consistent indentation (4 spaces)
5. ✅ Comment complex template logic

### Performance

1. ✅ Minimize template inheritance depth
2. ✅ Use `{% include %}` sparingly (prefer components)
3. ✅ Avoid complex template logic (move to views/tags)
4. ✅ Cache static content when appropriate

## Example: Complete Template

This example demonstrates proper use of the design system and Tailwind utilities:

```django
{% extends 'layout/base-logged.html' %}
{% load i18n %}

{% block title %}{% translate "Project List - Cosqua" %}{% endblock %}

{% block content %}
    <!-- h1 uses design system styles from base.css -->
    <h1>{% translate "My Projects" %}</h1>

    <!-- Form: mb-6 and flex gap-2 are Tailwind utilities for page-specific layout -->
    <form method="get" action="{% url 'audits:project_list' %}" class="mb-6">
        <div class="flex gap-2">
            <!-- input uses design system styles from base.css -->
            <input
                type="text"
                name="search"
                value="{{ request.GET.search }}"
                placeholder="{% translate 'Search by project name…' %}"
            >
            <!-- btn and btn-primary are design system classes from base.css -->
            <button type="submit" class="btn btn-primary">
                {% translate "Search" %}
            </button>
            {% if request.GET.search %}
                <!-- btn-secondary is a design system class from base.css -->
                <a href="{% url 'audits:project_list' %}" class="btn btn-secondary">
                    {% translate "Clear" %}
                </a>
            {% endif %}
        </div>
    </form>

    <!-- tiles and tile are design system classes from base.css -->
    <div class="tiles">
        {% for project in object_list %}
            <a href="{% url 'audits:project_detail' project.slug %}" class="tile {% cycle 'tile-even' 'tile-odd' %}">
                <!-- h2 uses design system styles from base.css -->
                <h2>{{ project.name }}</h2>
                {% if project.description %}
                    <p>{{ project.description|truncatewords:5 }}</p>
                {% endif %}
            </a>
        {% empty %}
            <!-- tile-empty is a design system class from base.css -->
            <div class="tile tile-empty">
                <p>
                    {% if request.GET.search %}
                        {% translate "No projects found matching your search." %}
                    {% else %}
                        {% translate "No projects yet." %}
                    {% endif %}
                </p>
            </div>
        {% endfor %}
    </div>
{% endblock content %}
```

**Key points:**

- ✅ Design system classes (`btn`, `btn-primary`, `tile`, `tiles`) come from `base.css`
- ✅ Tailwind utilities (`mb-6`, `flex`, `gap-2`) are used only for page-specific layout
- ✅ All colors are referenced from `tailwind.config.js` via design system classes
- ✅ Typography (`h1`, `h2`) uses design system styles from `base.css`

## Resources

- [Django Templates Documentation](https://docs.djangoproject.com/en/stable/topics/templates/)
- [Turbo Frames Guide](https://turbo.hotwired.dev/handbook/frames)
- [Stimulus Handbook](https://stimulus.hotwired.dev/handbook/introduction)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Django i18n Documentation](https://docs.djangoproject.com/en/stable/topics/i18n/)
