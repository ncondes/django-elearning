# eLearning Platform Style Guide

This document defines the visual design rules and standards for the eLearning platform.

## Design Philosophy

- **Minimalistic**: Clean, simple designs without unnecessary decoration
- **No gradients**: Use solid, flat colors only
- **Soft & Modern**: Neutral tones that are easy on the eyes
- **Consistent**: Same patterns and spacing throughout

---

## Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Primary Blue | `#5a9bd5` | Navbar, buttons, links, student badge, focus states |
| Primary Blue Hover | `#4a8bc5` | Button hover states |
| Primary Blue Light | `#e8f1f8` | Light backgrounds |

### Accent Colors
| Name | Hex | Usage |
|------|-----|-------|
| Accent Green | `#7cb87c` | Teacher badge, success/valid states |
| Accent Green Light | `#e8f5e8` | Light success backgrounds |

### Neutral Colors
| Name | Hex | Usage |
|------|-----|-------|
| Background Light | `#f8f9fa` | Page background |
| Background White | `#ffffff` | Cards, footer |
| Border Color | `#dee2e6` | Borders, dividers |

### Text Colors
| Name | Hex | Usage |
|------|-----|-------|
| Text Primary | `#333333` | Main text |
| Text Secondary | `#666666` | Secondary text |
| Text Muted | `#888888` | Timestamps, hints |

### Error Colors
| Name | Hex | Usage |
|------|-----|-------|
| Error Color | `#e8a5a5` | Error borders |
| Error Text | `#c25555` | Error messages |

---

## Typography

- **Font Family**: System default (Bootstrap 5 defaults)
- **Error Messages**: Regular weight (400), not bold
- **Labels**: Regular weight
- **Headings**: Default Bootstrap weights

---

## Border Radius

| Element | Radius |
|---------|--------|
| Cards | `0.5rem` (8px) |
| Card Headers | `0.5rem 0.5rem 0 0` |
| Buttons | Bootstrap default (~0.375rem) |
| Form Controls | Bootstrap default |
| Profile Photos | `50%` (circle) |

---

## Icons

We use **Bootstrap Icons** (v1.11.1)
- CDN: `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css`
- Browse: https://icons.getbootstrap.com/

### Role Icons
| Role | Icon Class |
|------|------------|
| Student | `bi-mortarboard` |
| Teacher | `bi-person-workspace` |

### Common Icons
| Purpose | Icon Class |
|---------|------------|
| User/Profile | `bi-person-fill` |
| Edit | `bi-pencil` |
| Calendar | `bi-calendar` |
| Clock/Time | `bi-clock` |
| Login | `bi-box-arrow-in-right` |
| Logout | `bi-box-arrow-right` |
| Add/Create | `bi-plus-lg` |
| Check/Confirm | `bi-check-lg` |

---

## Shadows

- **Cards**: `0 2px 8px rgba(0, 0, 0, 0.06)` — subtle, soft shadow
- **No heavy shadows** — keep it minimal

---

## Spacing

Follow Bootstrap 5 spacing utilities:
- `mb-3` for form fields
- `my-4` for main content container
- `py-4` for footer padding
- `gap-4` for flex gaps

---

## Components

### Cards
```css
.card {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 0.5rem;
}
```

### Buttons
- Primary: Solid `--primary-blue` background, white text
- Outline: `--primary-blue` border and text, fills on hover
- No gradients

### Badges
- Student: `--primary-blue` background, white text
- Teacher: `--accent-green` background, white text

### Form Controls
- Focus: `--primary-blue` border with soft blue shadow
- Valid: `--accent-green` border
- Invalid: `--error-color` border, `--error-text` message

---

## Form Validation

- **No HTML5 required attributes** — use `novalidate` on forms
- **Interactive validation** — validate on blur (field loses focus)
- **Clear on focus** — remove validation state when user focuses field
- **Error messages**: Regular font weight, displayed as bullet lists
- **Server-side validation** — always validate on backend too

---

## Footer

- White background
- Subtle top border
- Centered text, small font size
- No emojis — keep it professional but warm

Current text:
```
Crafted with care by Nicolas for the University of London
```
