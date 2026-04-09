# Design System Inspiration of Stripe

## 1. Visual Theme & Atmosphere

Stripe's website is the gold standard of fintech design — a system that feels simultaneously technical and luxurious. The page opens on a clean white canvas (`#ffffff`) with deep navy headings (`#061b31`) and a signature purple (`#533afd`) as the primary brand anchor. This isn't the cold purple of enterprise software; it's a rich, saturated violet that reads as confident and premium.

The custom `sohne-var` variable font is the defining element. Every text element enables `"ss01"` stylistic set for a distinctly geometric, modern feel. At display sizes (48–56px), sohne-var runs at weight 300 — an extraordinarily light weight that creates authority without shouting. Blue-tinted multi-layer shadows (`rgba(50,50,93,0.25)`) make elevation feel on-brand.

**Key Characteristics:**
- Light-mode native: `#ffffff` background, `#061b31` deep navy headings
- `sohne-var` with `"ss01"` on ALL text — the alternate glyphs define the brand
- Weight 300 as the signature headline weight — lightness as luxury
- Negative letter-spacing at display sizes (-1.4px at 56px, -0.96px at 48px)
- Blue-tinted multi-layer shadows: `rgba(50,50,93,0.25)` — elevation that feels brand-colored
- Conservative border-radius (4px–8px) — nothing pill-shaped on buttons or cards
- Ruby (`#ea2261`) and magenta (`#f96bee`) accents for gradients only
- `SourceCodePro` as monospace companion for code

## 2. Color Palette & Roles

### Primary
- **Stripe Purple** (`#533afd`): Primary CTA, links, interactive highlights
- **Deep Navy** (`#061b31`): Primary heading color — not black, a very dark blue
- **Pure White** (`#ffffff`): Page background, card surfaces

### Brand & Dark
- **Brand Dark** (`#1c1e54`): Dark sections, footer backgrounds
- **Dark Navy** (`#0d253d`): Near-black with blue undertone

### Accent (Decorative only)
- **Ruby** (`#ea2261`): Icons, alerts, gradient starts
- **Magenta** (`#f96bee`): Gradient midpoints, decorative highlights
- **Magenta Light** (`#ffd7ef`): Tinted surfaces for magenta-themed badges

### Interactive
- **Primary Purple** (`#533afd`): Links, active states
- **Purple Hover** (`#4434d4`): Hover on primary elements
- **Purple Light** (`#b9b9f9`): Subdued hover backgrounds

### Neutral Scale
- **Body** (`#64748d`): Secondary text, descriptions
- **Label** (`#273951`): Form labels, secondary headings
- **Success Green** (`#15be53`): Status badges (with 0.2-0.4 alpha for backgrounds)

### Borders & Shadows
- **Border Default** (`#e5edf5`): Standard card/divider border
- **Shadow Blue** (`rgba(50,50,93,0.25)`): Signature primary shadow
- **Shadow Black** (`rgba(0,0,0,0.1)`): Secondary shadow layer

## 3. Typography Rules

### Font Family
- **Primary**: `sohne-var` (fallback: `SF Pro Display`)
- **Monospace**: `SourceCodePro` (fallback: `SFMono-Regular`)
- **OpenType Features**: `"ss01"` on ALL sohne-var text. `"tnum"` for financial/tabular numbers.

### Hierarchy

| Role | Size | Weight | Letter Spacing | Notes |
|------|------|--------|----------------|-------|
| Display Hero | 56px | 300 | -1.4px | `"ss01"` — whisper-weight authority |
| Display Large | 48px | 300 | -0.96px | Secondary hero |
| Section Heading | 32px | 300 | -0.64px | Feature section titles |
| Sub-heading Large | 26px | 300 | -0.26px | Card headings |
| Sub-heading | 22px | 300 | -0.22px | Smaller section heads |
| Body Large | 18px | 300 | normal | Feature descriptions |
| Body | 16px | 300–400 | normal | Standard text |
| Button | 16px | 400 | normal | CTA text |
| Link | 14px | 400 | normal | Navigation links |
| Caption | 13px | 400 | normal | Small labels |
| Caption Tabular | 12px | 300–400 | -0.36px | `"tnum"` — financial data |
| Code | 12px SourceCodePro | 500 | normal | 2.00 line-height |

## 4. Component Stylings

### Buttons

**Primary Purple**
- Background: `#533afd`, Text: `#ffffff`, Padding: 8px 16px, Radius: 4px
- Font: 16px sohne-var weight 400 `"ss01"`, Hover: `#4434d4`

**Ghost / Outlined**
- Background: transparent, Text: `#533afd`
- Border: `1px solid #b9b9f9`, Radius: 4px
- Hover: `rgba(83,58,253,0.05)` background

**Neutral Ghost**
- Text: `rgba(16,16,16,0.3)`, Outline: `1px solid rgb(212,222,233)`, Radius: 4px

### Cards & Containers
- Background: `#ffffff`
- Border: `1px solid #e5edf5`
- Radius: 4px (tight), 5px (standard), 6px (comfortable), 8px (featured)
- Shadow: `rgba(50,50,93,0.25) 0px 30px 45px -30px, rgba(0,0,0,0.1) 0px 18px 36px -18px`

### Badges

**Success Badge**
- Background: `rgba(21,190,83,0.2)`, Text: `#108c3d`, Radius: 4px, Padding: 1px 6px
- Border: `1px solid rgba(21,190,83,0.4)`, Font: 10px weight 300

### Inputs & Forms
- Border: `1px solid #e5edf5`, Radius: 4px
- Focus: `1px solid #533afd`
- Label: `#273951` 14px, Text: `#061b31`, Placeholder: `#64748d`

### Navigation
- White sticky header, brand logotype left-aligned
- Links: sohne-var 14px weight 400 `#061b31` `"ss01"`
- CTA: purple button right-aligned

## 5. Layout Principles

### Spacing
- Base unit: 8px. Scale is dense at small end (every 2px from 4–12px) — reflecting financial UI precision.

### Border Radius Scale
- Standard (4px): Buttons, inputs, badges, cards — the workhorse
- Comfortable (5px–6px): Standard containers, nav
- Large (8px): Featured cards, hero elements
- **No pill shapes** (12px+) on interactive elements

### Whitespace Philosophy
- **Precision spacing**: Measured, purposeful. Not vast emptiness.
- **Dense data, generous chrome**: Financial tables are compact; surrounding UI is generous.
- **Section rhythm**: White ↔ Dark (`#1c1e54`) alternation for dramatic cadence.

## 6. Depth & Elevation

| Level | Treatment |
|-------|-----------|
| Ambient | `rgba(23,23,23,0.06) 0px 3px 6px` |
| Standard | `rgba(23,23,23,0.08) 0px 15px 35px` |
| Elevated | `rgba(50,50,93,0.25) 0px 30px 45px -30px, rgba(0,0,0,0.1) 0px 18px 36px -18px` |
| Deep | `rgba(3,3,39,0.25) 0px 14px 21px -14px, rgba(0,0,0,0.1) 0px 8px 17px -8px` |
| Focus Ring | `2px solid #533afd` outline |

**Shadow philosophy**: Blue-tinted primary (`rgba(50,50,93,0.25)`) + neutral secondary (`rgba(0,0,0,0.1)`) = chromatic depth. The negative spread (-30px, -18px) keeps elevation vertical and controlled.

## 7. Do's and Don'ts

### Do
- `font-feature-settings: "ss01"` on every sohne-var element — it IS the brand
- Weight 300 for all headlines — lightness is the signature
- Blue-tinted shadows `rgba(50,50,93,0.25)` for all elevated elements
- `#061b31` (deep navy) for headings — not `#000000`
- Border-radius 4px–8px — conservative rounding is intentional
- `"tnum"` for any tabular/financial number display

### Don't
- Don't use weight 600–700 for headlines — 300 is the brand voice
- Don't use large border-radius (12px+) on cards or buttons
- Don't use neutral gray shadows — always blue-tinted
- Don't skip `"ss01"` on sohne-var text
- Don't use pure black `#000000` for headings — always `#061b31`
- Don't use magenta/ruby for interactive elements — decorative/gradient only

## 8. Agent Prompt Guide

### Quick Color Reference
- CTA: `#533afd` (Stripe Purple)
- CTA Hover: `#4434d4`
- Background: `#ffffff`
- Heading: `#061b31` (Deep Navy)
- Body: `#64748d`
- Label: `#273951`
- Border: `#e5edf5`
- Dark Section: `#1c1e54`
- Success: `#15be53`

### Example Component Prompts
- "Hero on white. Headline 48px sohne-var weight 300, line-height 1.15, letter-spacing -0.96px, color #061b31, font-feature-settings 'ss01'. Body 18px weight 300 #64748d. CTA: #533afd bg, 4px radius, 8px 16px. Ghost: transparent, 1px solid #b9b9f9, #533afd text."
- "Card: white bg, 1px solid #e5edf5 border, 6px radius. Shadow: rgba(50,50,93,0.25) 0px 30px 45px -30px, rgba(0,0,0,0.1) 0px 18px 36px -18px. Title 22px sohne-var weight 300, -0.22px tracking, #061b31, 'ss01'. Body 16px weight 300 #64748d."
- "Dark section: #1c1e54 bg. Headline 32px sohne-var weight 300, -0.64px tracking, white, 'ss01'. Body 16px weight 300 rgba(255,255,255,0.7)."
- "Success badge: rgba(21,190,83,0.2) bg, #108c3d text, 4px radius, 1px 6px padding, 10px sohne-var weight 300, border 1px solid rgba(21,190,83,0.4)."
