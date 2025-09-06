# CSS Module Structure

This directory contains the modularized CSS files for the AI Storybook Generator.

## Directory Structure

```
css/
├── main.css              # Main entry point - imports all modules
├── base/                 # Base styles and variables
│   ├── variables.css     # CSS custom properties/variables
│   ├── reset.css        # CSS reset and base element styles
│   └── typography.css   # Typography and text styles
├── components/          # Reusable component styles
│   ├── buttons.css      # All button variants
│   ├── cards.css        # Card components
│   ├── forms.css        # Form elements and inputs
│   ├── modals.css       # Modal and overlay styles
│   └── loading.css      # Loading states and spinners
├── layouts/             # Layout-specific styles
│   ├── screens.css      # Screen/page layouts
│   ├── book-viewer.css  # Book viewer specific layout
│   └── grids.css        # Grid system layouts
├── themes/              # Theme-related styles
│   └── page-themes.css  # Story page theme backgrounds
└── utilities/           # Utility classes
    ├── animations.css   # Animation keyframes and classes
    ├── helpers.css      # Helper/utility classes
    ├── responsive.css   # Media queries and responsive design
    └── print.css        # Print-specific styles
```

## Usage

All CSS modules are imported through `main.css`. Simply include this single file in your HTML:

```html
<link rel="stylesheet" href="css/main.css">
```

## Module Descriptions

### Base
- **variables.css**: Defines all CSS custom properties used throughout the application
- **reset.css**: Normalizes default browser styles
- **typography.css**: Sets up font sizes, line heights, and text-related styles

### Components
- **buttons.css**: Primary, secondary, icon, navigation, and action button styles
- **cards.css**: Story cards, choice cards, and generic card layouts
- **forms.css**: Input fields, selects, textareas, and form groups
- **modals.css**: Error modals, menu overlays, and popup styles
- **loading.css**: Loading overlays, spinners, and progress indicators

### Layouts
- **screens.css**: Setup screen and book viewer screen layouts
- **book-viewer.css**: Page display, navigation, and book-specific layouts
- **grids.css**: Responsive grid systems for stories and choices

### Themes
- **page-themes.css**: Genre-based background themes (fantasy, adventure, sci-fi, mystery, comedy)

### Utilities
- **animations.css**: Page flip, slide, and fade animations
- **helpers.css**: Display utilities, margins, text alignment
- **responsive.css**: Mobile, tablet, and desktop breakpoints
- **print.css**: PDF export and print-specific styling

## Customization

To customize the application's appearance:

1. **Colors**: Edit variables in `base/variables.css`
2. **Fonts**: Modify typography in `base/typography.css`
3. **Themes**: Add new genre themes in `themes/page-themes.css`
4. **Breakpoints**: Adjust responsive design in `utilities/responsive.css`

## Best Practices

1. Keep modules focused on a single responsibility
2. Use CSS custom properties for values that might change
3. Follow the existing naming conventions
4. Test changes across all breakpoints
5. Ensure print styles work for PDF export