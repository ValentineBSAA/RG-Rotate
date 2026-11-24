# Beta verification

Build: Rotate Muse 0.1.0-beta, version code 1.

APK SHA-256: `3872fbb643677145c15c7f8534401a8bb6b49852100da6e0c5e3ad510819caa7`.

## Automated checks

- Gradle unit tests: **6 passed, zero failures/errors/skips**. Cover 12/24-hour clock formatting, timezone handling, seconds, bounded drag coordinates, timeout boundaries, and permitted media types.
- Android lint: **zero errors, 17 warnings**. Remaining warnings include older pinned dependencies/target SDK, procedural onDraw allocations, localization/RTL, and accessibility polish. No lint error baseline is used.
- APK assembly and Android v2 signature verification passed.
- Decoded manifest checked: unique package; no HOME category, network permission, broad storage, overlay, boot receiver or installation privileges.
- SDK 35 used for compilation; minimum API 29, target API 34. Physical target reports Android 12 / API 31.

## Observed on the connected RG Rotate

- ADB installation returned Success. First cold launch returned Status ok, approximately 1.6 seconds to launch.
- Native interface and fullscreen visually inspected on 720 × 720 screenshots. Theme and settings scrolling exercised with real touch input.
- Neon Nostalgia and Celestial Dream selected and displayed.
- Android Back and visible Exit returned from display.
- Original four-second H.264 test clip recorded from Muse, imported through Android's file picker, and played with no error. Active playback remained reported after more than a minute, covering multiple clip lengths. No claim of measured gapless boundaries or frame rate.
- Tiny original animated GIF imported through the picker and reported active looping with no error.
- 24-hour / seconds settings survived an app-only process restart; rendered clock observed with correct device minute/date. Restored 12-hour / no-seconds preferences after testing.
- Invalid private test MP4 triggered a useful error and procedural fallback. Only that task-created private test fixture was removed afterward.
- Window diagnostics confirmed dimmed `sbrt=0.08`, requested immersive fullscreen, 720 × 720 bounds.

- Clock drag positioning saved bounded coordinates and persisted the custom position.
- Selected two-minute timeout physically exited display mode, stopped playback and released keep-awake. Back then returned to Cocoon; HOME still resolved to Cocoon. Device left at the conservative tested two-minute timeout.

Hardware swivel activation remains **pending**, not enabled. A read-only physical event capture can inform future work; no automatic mechanism is claimed from a static snapshot or key event alone.

## Still pending

Physical open/close event mapping, automatic activation, stock clock conflict resolution, all framing/font/color combinations, detailed controller navigation and accessibility, long-run battery/temperature/frame-rate measurements, and cinematic character videos. Procedural themes are labeled demos. Existing emulator-session resume testing was deferred to avoid launching games or touching saves.

Local raw diagnostics, screenshots, test receipts, toolchain paths, signing keys and user data are excluded from the public project.
