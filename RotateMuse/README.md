# Rotate Muse · 0.1.0 beta

An independent, account-free Android display app for the 720 × 720 RG Rotate. Package `com.valentinebsaa.rotatemuse`. Android 10+; tested hardware target Android 12. It never registers as HOME.

## Implemented

- Native Media3 1.5.1 MP4 playback, silent repeat-one, Fit / Fill / Center crop, no playback controls. Decoder selection is delegated to Media3; actual codecs appear in Diagnostics.
- Animated GIF playback via Android AnimatedImageDrawable, decoded at a bounded target size.
- Original Neon Nostalgia and Celestial Dream procedural demos with moving atmospheric particles and flowing abstract silhouettes. These are **not finished cinematic character videos**, and do not provide natural blinking or fabric animation. Import your own licensed video for that experience.
- Local file picker, explicit import into private app storage, unique filenames, bounded streaming copy, empty/oversized file rejection, original media untouched. No broad storage permissions.
- Theme selection, immediate fullscreen preview, clock/date, 12/24-hour time, seconds, three fonts, four colors, opacity, shadow, positions, and drag positioning. Settings survive app restarts.
- Exit button and Android Back. No forced HOME launch. Video decoders released when hidden; playback never continues in a service.
- Default dimming after 30 seconds; default display ends after five minutes, releases keep-awake, and leaves Android's configured screen timeout in control. Does not force-lock the device.
- Diagnostics, offline operation, no account, analytics, network, overlay, accessibility, notification, or device-owner permissions.

## Build on Windows

Install JDK 17, Android SDK platform 35/build-tools 34.0.0 and Gradle 8.7 from their official publishers. Existing local tools can be reused. Media3 needs compile SDK 35; target SDK stays 34 and minimum SDK 29. AGP 8.5.2 is reused with its compile-35 recommendation warning suppressed. No wrapper binary or private signing key is committed.

```powershell
.\build.ps1 -Sdk 'C:\Android\Sdk' -Jdk 'C:\Java\jdk-17' -Gradle 'C:\Gradle\gradle-8.7\bin\gradle.bat'
```

This runs unit tests, Android lint and debug APK assembly. Output: `app/build/outputs/apk/debug/app-debug.apk`. Preserve your local debug key privately for subsequent updates. Do not publish the SDK/toolchain or signing key.

For no command windows, use `pythonw.exe build-quiet.py --sdk "C:\Android\Sdk" --jdk "C:\Java\jdk-17" --gradle "C:\Gradle\gradle-8.7\bin\gradle.bat"`. It writes `logs/build.log` and `logs/build-status.json`. Its Gradle subprocess is created without a console.

Optional install, when not gaming:

```powershell
.\install.ps1 -Adb 'C:\path\platform-tools\adb.exe'
```

No automatic launch or launcher changes. Never uninstall to resolve a signature mismatch without backing up app data.

## Physical acceptance checklist

All items below require actual device observation; automated helper tests do not prove these work physically.

1. Install, open Rotate Muse from Cocoon, select both themes, enter display, exit using Exit and Back. Check all touch targets and controller focus on the square screen.
2. Import an owned short H.264 MP4. Confirm silent playback over at least three loops, all aspect modes, and decoder diagnostics. Import an animated GIF separately. Try an invalid MP4: a useful message and procedural fallback should appear.
3. Change clock format, seconds, date, font, color and opacity. Preview; compare against system time. Drag clock to an edge. Exit/reopen and confirm saved settings.
4. Wait 30 seconds for dimming; wait five minutes for display exit. Confirm ordinary Android sleep afterward. Open another app while video runs and confirm Muse stops and frees decoder resources.
5. Confirm Cocoon remains HOME. Resume a saved emulator session. Confirm games/saves unaffected.
6. With user physically present, capture open/closed events using the diagnostics script. Repeat both directions at least three times. Observe stock clock and Cocoon behavior. **Swivel automation remains pending until signal and supported activation are proven together.**

## Hardware findings and limitations

The connected target reports RG Rotate, Android 12, 720 × 720, and Cocoon as HOME. Initial `getevent -lp` lists no SW_LID or SW_TABLET_MODE: gpio-keys includes F9/F12, but their relation to the swivel has not been demonstrated. Sensor snapshot does not establish a hinge/hall event. A static snapshot cannot prove a firmware broadcast absent. No synthetic key is treated as a real swivel test.

Cocoon documents its own closed-screen wallpaper/clock behavior: https://cocoon-shell.com/news/cocoon-3/ . No documented external Muse activation hook was established. Stock clock takeover and coexistence need physical testing. Android background activity restrictions apply: https://developer.android.com/guide/components/activities/background-starts . No workaround privileges are requested.

## Roadmap / handoff

Next: remaining physical acceptance, a reproducible swivel-event capture, supported Cocoon/vendor integration if available, media sorting/thumbnails, long-run battery/frame-rate measurement, accessibility and controller polish, and licensed/original cinematic theme videos. Smooth 24/30 FPS, seamless video boundaries, power usage and hardware swivel behavior are device tests, not guaranteed by a successful build. See VALIDATION.md for observed results.

Media3 implementation follows https://developer.android.com/media/media3/exoplayer/hello-world . No ROM, BIOS, personal configuration or private diagnostics are part of this source project.
