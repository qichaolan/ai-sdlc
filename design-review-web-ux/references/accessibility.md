# Accessibility baseline

The default target for design and review is WCAG 2.2 Level AA, unless the product specifies another standard. This checklist is a focused starting point, not an exhaustive conformance audit.

Before you assert that a success criterion (SC) fails, read it and check its exceptions. Cite the SC number for every confirmed finding. Reference baseline checked 2026-11-03. Don't call it the newest standard without checking again.

## Structure and semantics

- Check headings and landmarks, accessible names, labels and instructions, text alternatives, and table relationships (SC 1.3.1, 1.1.1, 2.4.6, 3.3.2, 4.1.2).
- Prefer native HTML semantics. Validate any custom widget against the WAI-ARIA Authoring Practices Guide (APG).
- Status messages must be announced without moving focus (SC 4.1.3). Don't announce every streamed token in AI or live-updating output. Announce meaningful milestones instead.
- SC 4.1.1 Parsing is obsolete in WCAG 2.2, so don't cite it.

## Keyboard and focus

- Complete each key task using only the keyboard (SC 2.1.1). Check for keyboard traps (SC 2.1.2).
- Check the focus order (SC 2.4.3), that focus is visible (SC 2.4.7), and that focus isn't fully hidden by sticky headers, banners, or overlays (SC 2.4.11).
- Escape should close dialogs and menus. Focus should return to the trigger when they close, and focus should stay inside a modal while it's open.
- Provide a skip link or another way to bypass repeated blocks (SC 2.4.1).

## Visual presentation

- Text contrast must be at least 4.5:1, or 3:1 for large text (SC 1.4.3, which has exceptions). Large text means at least 18 pt, or at least 14 pt bold (about 24 px and 18.66 px).
- UI components and meaningful graphics need 3:1 contrast against adjacent colors (SC 1.4.11). Assess this separately from text contrast.
- Never let color be the only way information is conveyed (SC 1.4.1).
- Text must resize to 200% without loss of content or function (SC 1.4.4).
- Content must reflow at 320 CSS px wide for vertically scrolling pages without two-dimensional scrolling (SC 1.4.10). Data tables, maps, and similar two-dimensional content are exempt.
- The layout must survive the user's text-spacing overrides (SC 1.4.12).
- Content that appears on hover or focus, such as tooltips and popovers, must be dismissible, hoverable, and persistent (SC 1.4.13).

## Pointer and touch

- Targets must be at least 24 × 24 CSS px, unless the spacing, inline, or equivalent exceptions apply (SC 2.5.8, AA).
- Prefer about 44 × 44 CSS px for touch controls. That size matches SC 2.5.5 (AAA), so present it as a recommendation, not as the AA minimum.
- Any dragging action needs a single-pointer alternative (SC 2.5.7). Path-based or multipoint gestures need simple alternatives (SC 2.5.1).

## Forms, errors, and authentication

- Identify errors in text (SC 3.3.1) and suggest a fix when one is known (SC 3.3.3). Prevent errors on legal, financial, and data-changing submissions (SC 3.3.4).
- Don't make users re-enter information they already gave in the same process (SC 3.3.7).
- Authentication must not depend on a cognitive function test unless an alternative or assistance is offered, such as paste, password managers, or passkeys (SC 3.3.8).

## Motion and media

- Auto-moving content needs pause, stop, or hide controls (SC 2.2.2).
- Honor `prefers-reduced-motion`. That's good practice, and it covers motion triggered by interaction (SC 2.3.3, AAA), so present it as a recommendation rather than an AA failure.
- Media needs captions and alternatives that fit its type (SC 1.2.x).

## Testing approach

- Automated tools such as axe and Lighthouse catch only part of the issues. Follow them with manual checks of the key tasks.
- Never infer conformance from an automated score, a screenshot, or a small sample.
- Name the assistive technology and browser pairs you actually used, for example VoiceOver with Safari or NVDA with Firefox, and list the checks you didn't resolve.
