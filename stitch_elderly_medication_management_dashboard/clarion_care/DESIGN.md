---
name: Clarion Care
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1c1b1b'
  on-surface-variant: '#3d4a3d'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#6d7b6c'
  outline-variant: '#bccbb9'
  surface-tint: '#006e2f'
  primary: '#006e2f'
  on-primary: '#ffffff'
  primary-container: '#22c55e'
  on-primary-container: '#004b1e'
  inverse-primary: '#4ae176'
  secondary: '#0058be'
  on-secondary: '#ffffff'
  secondary-container: '#2170e4'
  on-secondary-container: '#fefcff'
  tertiary: '#735c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#cfa800'
  on-tertiary-container: '#4f3e00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6bff8f'
  primary-fixed-dim: '#4ae176'
  on-primary-fixed: '#002109'
  on-primary-fixed-variant: '#005321'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a42'
  on-secondary-fixed-variant: '#004395'
  tertiary-fixed: '#ffe083'
  tertiary-fixed-dim: '#eec200'
  on-tertiary-fixed: '#231b00'
  on-tertiary-fixed-variant: '#574500'
  background: '#fcf9f8'
  on-background: '#1c1b1b'
  surface-variant: '#e5e2e1'
typography:
  display-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.5'
  body-md:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 20px
    fontWeight: '400'
    lineHeight: '1.5'
  label-lg:
    fontFamily: Atkinson Hyperlegible Next
    fontSize: 18px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-page: 40px
  touch-target-min: 64px
  stack-gap: 16px
---

## Brand & Style
The design system focuses on cognitive clarity, physical accessibility, and emotional reassurance for elderly users managing medication. The brand personality is dependable, patient, and highly legible, prioritizing functional utility over decorative flair.

The style is **Modern Corporate with a High-Accessibility focus**. It utilizes large touch targets, high-contrast ratios, and a clean, flat-design aesthetic to reduce visual noise. Every element is designed to minimize "choice paralysis" and provide immediate, unambiguous feedback regarding medication status. The interface avoids complex gestures, relying entirely on simple, high-affordance taps.

## Colors
The color palette is functionally mapped to user actions and system states:
- **Off-white (#F9F9F9):** Used for the primary background to reduce screen glare and eye fatigue compared to pure white.
- **High-Contrast Dark Gray (#1A1A1A):** All text and critical iconography utilize this color to meet or exceed WCAG AAA contrast requirements.
- **Action Green (#22C55E):** Reserved exclusively for "Take Medication" or "Confirm" actions.
- **Schedule Blue (#3B82F6):** Identifies upcoming doses and scheduled items.
- **Active Yellow (#FACC15):** A high-visibility "Alert" color used only when the machine is currently dispensing or requires immediate attention.
- **Empty Gray (#E5E7EB):** Indicates past events or empty medication slots, visually receding to prioritize current tasks.

## Typography
This design system utilizes **Atkinson Hyperlegible Next**, specifically engineered for low-vision readers. The typeface focuses on letterform distinction (e.g., differentiating 'I', '1', and 'l') to prevent medication errors.

- **Scale:** All font sizes are significantly enlarged to ensure readability at arm's length (tablet-on-stand distance).
- **Weight:** Use Bold (700) or Extra Bold (800) for all headings to maintain high stroke contrast against the background.
- **Spacing:** Increased line-height (1.5) for body text prevents "crowding" of lines, which can be difficult for patients with macular degeneration.

## Layout & Spacing
The layout follows a **60/40 Split Tablet Model** optimized for landscape orientation:
- **Left Pane (60%):** Primary focus area. Displays the "Next Dose" or "Active Action" in a large, hero-style card.
- **Right Pane (40%):** Secondary information. Displays the upcoming daily schedule or historical logs.

**Spacing Principles:**
- **Ample Margins:** 40px page margins prevent accidental edge-taps when picking up the tablet.
- **Large Touch Targets:** No interactive element is smaller than 64px, ensuring ease of use for patients with tremors or arthritis.
- **Vertical Rhythm:** Content is organized in a clear, linear stack with 16px to 24px gaps to maintain a clear visual hierarchy.

## Elevation & Depth
To aid users with diminished depth perception, the design system uses **Tactile Affordance** through pronounced, physical-style shadows:
- **Interactive Depth:** Buttons use a "lifted" effect with a 15% opacity dark gray shadow (8px offset) to clearly signal they are tappable.
- **Surface Layering:** The primary action card on the left pane uses a slightly higher elevation than the secondary schedule on the right to draw the eye first.
- **Flat Containers:** Background containers for non-interactive data use 2px solid borders (#E5E7EB) instead of shadows to avoid visual clutter and maintain the flat-design aesthetic.

## Shapes
The shape language uses **Rounded (0.5rem / 8px)** corners. This creates a friendly, non-clinical feel while maintaining the structural integrity of the high-contrast grid. 

- **Primary Buttons:** Use 1rem (rounded-lg) for a softer, more inviting appearance.
- **Selection Chips:** Use 2rem (pill-shaped) to distinguish them from actionable buttons.
- **Cards:** Use 1.5rem (rounded-xl) to create a clear "container" feel for grouped information.

## Components
- **Action Buttons:** Large-scale components (min-height 80px) with center-aligned, bold text. The "Take Now" button is Action Green with a white label for maximum visibility.
- **Status Indicators:** Use a "Circle + Icon + Label" format. Never rely on color alone; always include text (e.g., a green checkmark icon with the word "Taken").
- **Medication Cards:** High-contrast cards featuring a large-scale icon of the pill shape/color and the name of the medication in Headline-MD.
- **Schedule List:** A vertical timeline with large 48px connection lines between time-slots to show the progression of the day.
- **Input Fields:** Oversized numeric keypads for PIN entry or dosage adjustments, featuring high-contrast borders and immediate tactile (haptic/visual) feedback on tap.
- **Alert Modal:** A full-screen overlay using the Active Yellow as a border-accent, forcing the user to acknowledge critical system notifications.