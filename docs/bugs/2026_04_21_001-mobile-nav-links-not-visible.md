# Bug 2026_04_21_001 — Learn/Games Navigation Links Not Visible on Certain Mobile Devices

## Description

The fixed bottom navigation bar containing the "Learn" (📚) and "Games" (🎮) links is cut off and not visible on certain mobile devices (e.g., iPhone 14), while it works correctly on others (e.g., Samsung Galaxy S8). The bottom portion of the viewport is clipped, hiding the navigation bar.

## Steps to Reproduce

1. Open the app on an iPhone 14 (or similar device with a home indicator / no physical home button) using Safari or Chrome.
2. Navigate to any page (e.g., the phonics categories page at `/phonics/`).
3. Look for the bottom navigation bar with "Learn" and "Games" links.

## Expected Behavior

A fixed bottom navigation bar should appear at the bottom of the visible viewport with two tappable links: "📚 Learn" (`/phonics/`) and "🎮 Games" (`/games/`), properly inset above any device system UI (home indicator, gesture bar).

## Actual Behavior

On iPhone 14 (and other iPhones without a physical home button), the bottom navigation bar is hidden behind the device's home indicator / safe area. The nav is rendered at `bottom: 0` which sits underneath the system UI, making it invisible or untappable. The Samsung Galaxy S8 is unaffected because its system navigation buttons are outside the web viewport.

## Fix

The root cause is that the layout does not account for the iOS safe area insets on devices with a home indicator (iPhone X and later). There are three issues:

1. **Missing `viewport-fit=cover`** in `templates/base.html` — the `<meta name="viewport">` tag uses `width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no` but lacks `viewport-fit=cover`. Without this, `env(safe-area-inset-bottom)` has no effect and iOS Safari clips the bottom of the viewport at the safe area boundary.

2. **`.app-nav` does not use safe-area padding** in `static/css/layout.css` — the nav is positioned with `bottom: 0` but has no `padding-bottom: env(safe-area-inset-bottom)`, so it sits behind the home indicator on notched iPhones.

3. **`body` bottom padding ignores safe area** in `static/css/layout.css` — `body { padding-bottom: 70px; }` does not add the safe-area inset, so main content can also be hidden behind the nav + safe area.

### Recommended changes

1. In `templates/base.html`, add `viewport-fit=cover` to the viewport meta tag:

   ```html
   <meta
     name="viewport"
     content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover"
   />
   ```

2. In `static/css/layout.css`, add safe-area padding to `.app-nav`:

   ```css
   .app-nav {
     padding-bottom: calc(0.5rem + env(safe-area-inset-bottom, 0px));
   }
   ```

3. In `static/css/layout.css`, update the body bottom padding to account for the safe area:
   ```css
   body {
     padding-bottom: calc(70px + env(safe-area-inset-bottom, 0px));
   }
   ```

### Devices affected

- **Affected**: iPhone X, iPhone 11, iPhone 12, iPhone 13, iPhone 14, iPhone 15 (any device with home indicator / notch / Dynamic Island)
- **Not affected**: Samsung Galaxy S8, and other Android devices where system navigation is outside the web viewport; older iPhones with a physical home button
