# LINK Studio Design Tokens

Internal builder tools use Studio aesthetic: precision, clarity, density.

## Colors

```css
--studio-bg: #0a0a0a;
--studio-surface: #141414;
--studio-surface-hover: #1a1a1a;
--studio-border: #2a2a2a;
--studio-text: #e8e8e8;
--studio-text-dim: #8a8a8a;
--studio-accent: #00a8ff;
--studio-accent-dim: #0088cc;
--studio-success: #00d68f;
--studio-warning: #ffa726;
--studio-error: #ff5252;
--studio-purple: #a855f7;
```

## Typography

- **Font**: system-ui, -apple-system, "Segoe UI", sans-serif
- **Sizes**: 11px (caption), 13px (body), 14px (label), 16px (heading)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold)
- **Line height**: 1.4 for body, 1.2 for headings

## Spacing

- Base unit: 8px
- Table padding: 8px (cell), 12px (header)
- Section gap: 16px
- Page padding: 24px

## Components

### Table / Spreadsheet
- Dense, editable cells
- 1px borders in --studio-border
- Hover row: --studio-surface-hover
- Fixed headers with sticky positioning
- Monospace for numbers/codes

### Buttons
- Height: 32px
- Padding: 0 16px
- Border-radius: 4px
- Background: --studio-accent
- Hover: --studio-accent-dim

### Navigation
- Sidebar: 240px width
- Item height: 36px
- Active: border-left 3px --studio-accent
