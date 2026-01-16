# Tailwind CSS Design System

This document explains how Tailwind CSS is configured and used to build a consistent design system in the webapp.

## Overview

The design system is built using Tailwind CSS with a custom configuration that extends Tailwind's default theme with project-specific design tokens. The approach combines:

- **Custom theme configuration** in `tailwind.config.js` for design tokens (colors, spacing, etc.)
- **Component-based CSS modules** in `static/to_compile/css/` using Tailwind's `@apply` directive
- **Direct utility classes** in templates when component classes aren't sufficient

## Configuration

### Theme Customization

The `tailwind.config.js` file defines a custom color palette that serves as the foundation of the design system:

```javascript
theme: {
  colors: {
    // Layout colors
    bg_layout: "#96B9D4",      // Header, sidebar, footer background
    bg_content: "#EDF5FB",     // Main content background

    // Text and borders
    border: "#9E9E9E",         // Input borders, dividers
    content: "#424242",        // Main content text color

    // Link colors
    link: "#0066cc",
    hover_link: "#0052a3",
    active_link: "#0052a3",

    // Navigation link colors
    nav_link: "#424242",
    nav_hover_link: "#212121",
    nav_active_link: "#212121",

    // Primary button colors
    primary: "#2563eb",
    primary_hover: "#1d4ed8",
    primary_text: "white",
    primary_hover_text: "#F5F5F5",

    // Secondary button colors
    secondary: "#F7FAFD",
    secondary_hover: "#EDF5FB",
    secondary_text: "#424242",
    secondary_hover_text: "#212121",

    // Danger/error colors
    danger: "#DC2626",
    danger_hover: "#B91C1C",
    danger_text: "white",
    danger_hover_text: "#F5F5F5",

    // Table/list alternating colors
    odd: "#E8F0F9",
    even: "#E4EBF9",

    // Additional semantic colors
    info: "#000091",
    dark: "#3c3d40",
    // ... standard colors
  }
}
```

### Key Configuration Options

- **`preflight: false`**: Tailwind's base styles are disabled to avoid conflicts with existing styles
- **`content`**: Configured to scan templates and TypeScript/JavaScript files for class usage
- **`plugins`**: Includes `tailwindcss-animate` for animation utilities

## Architecture

### CSS Module Structure

The CSS is organized into modular files, each responsible for a specific component or area:

```
static/to_compile/css/
├── base.css          # Base styles and imports
├── buttons.css       # Button components
├── forms.css         # Form inputs and labels
├── cards.css         # Card components
├── dropdown.css      # Dropdown menus
├── headers.css       # Header navigation
├── footers.css       # Footer styles
├── links.css         # Link styles
├── tiles.css         # Tile/list components
├── blocks.css        # Content blocks
├── page-headers.css  # Page heading styles
├── danger-zone.css   # Danger/error zones
├── markdown-zone.css # Markdown content areas
├── signup-login.css  # Authentication pages
└── main.css          # Main layout styles
```

### Base Styles (`base.css`)

The `base.css` file serves as the entry point:

1. **Imports all component modules** in the correct order
2. **Defines global base styles** using `@apply`:
   - `body`: Sets font, background, and text color
   - `p`: Sets paragraph spacing

### Component Pattern

Components are built using Tailwind's `@apply` directive, which allows you to compose utility classes into reusable CSS classes:

```css
/* Example from buttons.css */
.btn-primary {
  @apply bg-primary text-primary_text border-border
         hover:bg-primary_hover hover:text-primary_hover_text
         transition;
}
```

This pattern provides:

- **Consistency**: All buttons share the same base styles
- **Maintainability**: Changes to button styles happen in one place
- **Flexibility**: Can still use utility classes directly when needed

## Usage Guidelines

### When to Use Component Classes

Use predefined component classes (e.g., `.btn-primary`, `.card`, `.tile`) when:

- The component matches an existing pattern
- You want consistency across the application
- The component needs complex styling that benefits from abstraction

**Example:**

```html
<button class="btn btn-primary">Save</button>
<div class="card">Card content</div>
```

### When to Use Utility Classes Directly

Use Tailwind utility classes directly when:

- You need one-off styling that doesn't warrant a component
- You're prototyping and haven't decided on a pattern yet
- The component classes don't quite fit your needs

**Example:**

```html
<div class="flex items-center gap-4 p-6 bg-white rounded-lg">Custom layout</div>
```

### Extending the Design System

#### Adding New Colors

1. Add the color to `tailwind.config.js` in the `theme.colors` object
2. Use it in component CSS files with `@apply bg-your-color`
3. Or use it directly in templates: `bg-your-color`

#### Creating New Components

1. Create a new CSS file in `static/to_compile/css/` (e.g., `modals.css`)
2. Define component classes using `@apply`:

   ```css
   .modal {
     @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center;
   }

   .modal-content {
     @apply bg-white rounded-lg p-6 max-w-md w-full;
   }
   ```

3. Import the new file in `base.css`
4. Document the component in this file or in component-specific documentation

#### Modifying Existing Components

1. Locate the relevant CSS file in `static/to_compile/css/`
2. Update the `@apply` directives as needed
3. Test across all usages of the component
4. Consider backward compatibility if the component is widely used

## Component Reference

### Buttons

**Classes:**

- `.btn` - Base button styles
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.btn-danger` - Destructive action button

**Usage:**

```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary Action</button>
<button class="btn btn-danger">Delete</button>
```

### Forms

**Styles applied to:**

- `label` - Form labels
- `input` - Text inputs
- `textarea` - Text areas
- `select` - Select dropdowns
- `.helptext` - Help text

**Usage:**

```html
<label>Email</label>
<input type="email" />
<span class="helptext">Enter your email address</span>
```

### Cards

**Classes:**

- `.card` - Card container

**Usage:**

```html
<div class="card">Card content</div>
```

### Tiles

**Classes:**

- `.tiles` - Container for tile grid
- `.tile` - Individual tile
- `.tile-odd` - Odd-numbered tile styling
- `.tile-even` - Even-numbered tile styling
- `.tile-empty` - Empty state tile

**Usage:**

```html
<div class="tiles">
  <a href="#" class="tile tile-odd">Tile 1</a>
  <a href="#" class="tile tile-even">Tile 2</a>
</div>
```

### Layout

**Main layout structure:**

- `main .main-layout` - Main container with sidebar
- `main .main-layout aside` - Sidebar navigation
- `main .content` - Main content area
- `main .content-center` - Centered content area

**Usage:**

```html
<main>
  <div class="main-layout">
    <aside>
      <nav>
        <a href="#" class="active">Link</a>
      </nav>
    </aside>
    <div class="content">Content here</div>
  </div>
</main>
```

### Dropdowns

**Classes:**

- `.dropdown-menu-wrapper` - Dropdown container
- `.dropdown-menu` - Dropdown menu
- `.dropdown-item` - Menu item
- `.dropdown-item.active` - Active menu item
- `.dropdown-item-create` - Special "create" menu item

### Danger Zones

**Classes:**

- `.danger-zone` - Container for dangerous actions

**Usage:**

```html
<div class="danger-zone">
  <h3>Dangerous Action</h3>
  <button class="btn btn-danger">Delete</button>
</div>
```

## Best Practices

1. **Use semantic color names**: Prefer `bg-primary` over `bg-blue-600` for better maintainability
2. **Compose with `@apply`**: Create component classes for repeated patterns
3. **Keep components focused**: Each CSS file should handle one concern
4. **Document new patterns**: When creating new components, document them here
5. **Test across breakpoints**: Ensure components work on mobile (`lg:` prefixes indicate desktop-only styles)
6. **Maintain color consistency**: Use theme colors rather than hardcoded hex values

## Development Workflow

1. **Make changes** to CSS files in `static/to_compile/css/`
2. **Build assets**: Run `make npm-build` or `make npm-watch` for development
3. **Test in templates**: Verify changes work as expected
4. **Update documentation**: If adding new components or patterns, update this file

## Color System Philosophy

The color system is organized around semantic meaning rather than visual appearance:

- **Layout colors** (`bg_layout`, `bg_content`) define the page structure
- **Semantic colors** (`primary`, `secondary`, `danger`) define component states
- **State colors** (`hover_*`, `active_*`) define interactive states
- **Text colors** (`*_text`) ensure proper contrast

This approach makes it easier to:

- Update the entire color scheme by changing values in `tailwind.config.js`
- Maintain accessibility by ensuring text colors have proper contrast
- Understand component behavior through color names

## Accessibility Considerations

- **Contrast**: All text colors are paired with appropriate background colors for WCAG compliance
- **Focus states**: Form inputs include focus styles (`focus:border-primary`)
- **Disabled states**: Buttons have disabled styles (`cursor-not-allowed`)
- **Semantic HTML**: Component classes work with semantic HTML elements
