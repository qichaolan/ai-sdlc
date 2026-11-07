# Cross-platform coverage

Build the support matrix from product requirements and audience data. If neither exists, propose the coverage below and label it provisional, so nobody reads it as a contractual support policy.

| Axis | Representative coverage | Verify |
| --- | --- | --- |
| Small phone | 320 CSS px as a stress case; a typical phone at about 390 CSS px | Reflow, navigation, forms, long labels, fixed controls |
| Tablet | About 768 CSS px, portrait and landscape | Layout transitions, touch, an optional keyboard |
| Desktop | About 1280–1440 CSS px, in narrow and wide windows | Reading width, density, keyboard efficiency, resizing |
| Browser engines | Chromium, Firefox (Gecko), Safari (WebKit) | Layout, controls, focus, dialogs, supported APIs |
| OS and device | Windows and macOS desktops; iOS/iPadOS and Android mobile | Fonts, native controls, the virtual keyboard, viewport changes |
| Input and assistive tech | Mouse, touch, keyboard, representative screen readers | Equal task completion without relying only on hover or dragging |
| User preferences | Reduced motion, forced colors or high contrast, supported themes | Visible state, focus, contrast, essential information |
| Content and network | Long text, localization, RTL if in scope, slow or interrupted network | Wrapping, reading order, recovery, state preservation |

Mark each row **Tested**, **Partially tested**, **Not tested**, or **Not applicable**. Give the evidence and the remaining risk, and record actual version numbers. Test high-risk journeys on distinct engines and device classes. Sample lower-risk combinations by risk, and explain any reduced coverage.

## Testing methods and what they establish

- Viewport emulation, engine automation, real-device testing, and assistive-technology testing are different things, so report which one you used.
- A resized desktop browser doesn't establish iOS behavior.
- An automated WebKit run doesn't establish Safari behavior.

## Adaptive design rules

- Treat the sample widths as test points, not prescribed breakpoints. Put breakpoints where the content or interaction needs to change, and test the widths between them.
- Preserve task capability and the priority of information across layouts. Adapt navigation, tables, toolbars, and secondary content on purpose rather than shrinking the desktop UI.
- Prefer feature detection and progressive enhancement. Give any capability that falls outside the support matrix a usable fallback.
- Account for safe areas, mobile browser chrome, on-screen keyboards, orientation changes, and scrollable overlays. Keep focused fields and primary actions reachable while the keyboard is open.
- Offer discoverable alternatives to hover, complex gestures, and drag-only actions. Respect each platform's shortcut conventions, and don't override browser controls.
- Preserve meaningful URLs, back and forward behavior, recovery after a refresh, and deep links where appropriate. Keep confidential data out of URLs.
