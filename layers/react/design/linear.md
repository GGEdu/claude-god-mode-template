# Design System Inspiration of Linear

## 1. Visual Theme & Atmosphere

Linear's website exemplifies dark-mode-first product design — a near-black canvas (`#08090a`) where content emerges like starlight. The impression is one of extreme precision: every element exists in a carefully calibrated hierarchy of luminance, from barely-visible borders (`rgba(255,255,255,0.05)`) to soft text (`#f7f8f8`). This represents darkness as the native medium, where information density is managed through subtle gradations of white opacity rather than color variation.

The typography system is built entirely on Inter Variable with OpenType features `"cv01"` and `"ss03"` enabled globally, giving the typeface a cleaner, more geometric character. Inter is used at a remarkable range of weights — from 300 (light body) through 510 (medium, Linear's signature weight) to 590 (semibold emphasis). At display sizes (72px, 64px, 48px), Inter uses aggressive negative letter-spacing (-1.584px to -1.056px), creating compressed, authoritative headlines.

The color system is almost entirely achromatic — dark backgrounds with white/gray text — punctuated by a single brand accent: Linear's signature indigo-violet (`#5e6ad2` for backgrounds, `#7170ff` for interactive accents). This accent color is used sparingly and intentionally, appearing only on CTAs, active states, and brand elements.

**Key Characteristics:**
- Dark-mode-native: `#08090a` marketing background, `#0f1011` panel background, `#191a1b` elevated surfaces
- Inter Variable with `"cv01", "ss03"` globally — geometric alternates for cleaner aesthetics
- Signature weight 510 (between regular and medium) for most UI text
- Aggressive negative letter-spacing at display sizes (-1.584px at 72px, -1.056px at 48px)
- Brand indigo-violet: `#5e6ad2` (bg) / `#7170ff` (accent) / `#828fff` (hover) — the only chromatic color
- Semi-transparent white borders throughout: `rgba(255,255,255,0.05)` to `rgba(255,255,255,0.08)`
- Button backgrounds at near-zero opacity: `rgba(255,255,255,0.02)` to `rgba(255,255,255,0.05)`
- Multi-layered shadows with inset variants for depth on dark surfaces
- Success green (`#27a644`, `#10b981`) used only for status indicators

## 2. Color Palette & Roles

### Background Surfaces
- **Marketing Black** (`#010102` / `#08090a`): The deepest background — the canvas for hero sections and marketing pages.
- **Panel Dark** (`#0f1011`): Sidebar and panel backgrounds.
- **Level 3 Surface** (`#191a1b`): Elevated surface areas, card backgrounds, dropdowns.
- **Secondary Surface** (`#28282c`): Hover states and slightly elevated components.

### Text & Content
- **Primary Text** (`#f7f8f8`): Near-white. Default text color.
- **Secondary Text** (`#d0d6e0`): Cool silver-gray for body text and descriptions.
- **Tertiary Text** (`#8a8f98`): Muted gray for placeholders and metadata.
- **Quaternary Text** (`#62666d`): Timestamps, disabled states, subtle labels.

### Brand & Accent
- **Brand Indigo** (`#5e6ad2`): Primary brand color — CTA backgrounds, key interactive surfaces.
- **Accent Violet** (`#7170ff`): Links, active states, selected items.
- **Accent Hover** (`#828fff`): Hover states on accent elements.

### Border & Divider
- **Border Subtle** (`rgba(255,255,255,0.05)`): Ultra-subtle semi-transparent border — the default.
- **Border Standard** (`rgba(255,255,255,0.08)`): Cards, inputs, code blocks.
- **Border Primary** (`#23252a`): Solid dark border for prominent separations.

## 3. Typography Rules

### Font Family
- **Primary**: `Inter Variable` (fallback: `SF Pro Display, -apple-system, system-ui`)
- **Monospace**: `Berkeley Mono` (fallback: `ui-monospace, SF Mono, Menlo`)
- **OpenType Features**: `"cv01", "ss03"` on ALL text globally.

### Hierarchy

| Role | Size | Weight | Letter Spacing | Notes |
|------|------|--------|----------------|-------|
| Display XL | 72px | 510 | -1.584px | Hero headlines |
| Display Large | 64px | 510 | -1.408px | Secondary hero |
| Display | 48px | 510 | -1.056px | Section headlines |
| Heading 1 | 32px | 400 | -0.704px | Major section titles |
| Heading 2 | 24px | 400 | -0.288px | Sub-section headings |
| Heading 3 | 20px | 590 | -0.24px | Card headers |
| Body Large | 18px | 400 | -0.165px | Feature descriptions |
| Body | 16px | 400 | normal | Standard reading text |
| Body Medium | 16px | 510 | normal | Navigation, labels |
| Small | 15px | 400 | -0.165px | Secondary body |
| Caption | 13px | 510 | -0.13px | Metadata, timestamps |
| Label | 12px | 400–590 | normal | Button text, small labels |
| Mono Body | 14px Berkeley Mono | 400 | normal | Code blocks |

## 4. Component Stylings

### Buttons

**Ghost Button (Default)**
- Background: `rgba(255,255,255,0.02)`, Text: `#e2e4e7`, Radius: 6px
- Border: `1px solid rgb(36, 40, 44)`

**Primary Brand Button**
- Background: `#5e6ad2`, Text: `#ffffff`, Radius: 6px, Hover: `#828fff`

**Pill Button**
- Background: transparent, Radius: 9999px, Border: `1px solid #23252a`

### Cards & Containers
- Background: `rgba(255,255,255,0.02)` to `rgba(255,255,255,0.05)` (always translucent)
- Border: `1px solid rgba(255,255,255,0.08)`
- Radius: 8px (standard), 12px (featured), 22px (large panels)

### Inputs
- Background: `rgba(255,255,255,0.02)`, Border: `1px solid rgba(255,255,255,0.08)`, Radius: 6px

## 5. Layout Principles

### Spacing
- Base unit: 8px. Scale: 4px, 8px, 12px, 16px, 24px, 32px

### Border Radius Scale
- Micro (2px): Inline badges, toolbar buttons
- Comfortable (6px): Buttons, inputs
- Card (8px): Cards, dropdowns
- Panel (12px): Featured cards, panels
- Full Pill (9999px): Filter chips, status tags
- Circle (50%): Icon buttons, avatars

## 6. Depth & Elevation

| Level | Treatment |
|-------|-----------|
| Surface | `rgba(255,255,255,0.05)` bg + `1px solid rgba(255,255,255,0.08)` border |
| Elevated | `rgba(0,0,0,0.4) 0px 2px 4px` shadow |
| Dialog | Multi-layer: `rgba(0,0,0,0.08) 0px 0px 1px, rgba(0,0,0,0.07) 0px 1px 1px, rgba(0,0,0,0.04) 0px 3px 2px` |

Elevation = background luminance stepping, not shadow darkness.

## 7. Do's and Don'ts

### Do
- `font-feature-settings: "cv01", "ss03"` on ALL Inter text
- Weight 510 as default emphasis — it's Linear's signature
- Near-black backgrounds: `#08090a` marketing, `#0f1011` panels, `#191a1b` elevated
- Semi-transparent white borders (`rgba(255,255,255,0.05-0.08)`)
- Button bg: `rgba(255,255,255,0.02-0.05)` — nearly transparent
- `#f7f8f8` for primary text (not pure `#ffffff`)

### Don't
- Don't use pure white as text — too harsh
- Don't use solid colored backgrounds for buttons
- Don't use brand indigo decoratively — CTAs only
- Don't skip `"cv01", "ss03"` OpenType features
- Don't use weight 700 — max is 590
- Don't use drop shadows for elevation — use luminance stepping

## 8. Agent Prompt Guide

### Quick Color Reference
- CTA: `#5e6ad2` (Brand Indigo)
- Background: `#08090a` (Marketing Black)
- Panel: `#0f1011`
- Surface: `#191a1b`
- Heading: `#f7f8f8`
- Body: `#d0d6e0`
- Muted: `#8a8f98`
- Accent: `#7170ff`
- Border: `rgba(255,255,255,0.08)`

### Example Component Prompts
- "Hero on `#08090a`. Headline 48px Inter Variable weight 510, letter-spacing -1.056px, color `#f7f8f8`, font-feature-settings `'cv01','ss03'`. Body 18px weight 400 `#8a8f98`. CTA: `#5e6ad2` bg, 6px radius. Ghost: `rgba(255,255,255,0.02)` bg, `1px solid rgba(255,255,255,0.08)`."
- "Card: `rgba(255,255,255,0.02)` bg, `1px solid rgba(255,255,255,0.08)` border, 8px radius. Title 20px weight 590, -0.24px tracking, `#f7f8f8`. Body 15px weight 400 `#8a8f98`."
- "Nav: `#0f1011` bg, Inter 13px weight 510 `#d0d6e0`. CTA `#5e6ad2` right-aligned. Bottom: `1px solid rgba(255,255,255,0.05)`."
