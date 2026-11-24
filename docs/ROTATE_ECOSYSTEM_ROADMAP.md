# RG Rotate — Native experience and Rotate application ecosystem

Updated 2026-11-24. This is the forward-looking handheld roadmap, alongside the existing [Retro Library Studio roadmap](ROADMAP.md). Continue the newest local Codex workspace, not an older source ZIP. Device-side application sources and latest installed build have not yet been reconciled with this repository; this document records owner-reported acceptance and planned requirements, not a claim that the Android sources are published here.

## Product vision and locked decisions

- Keep stock Android 12 / Anbernic RG Rotate firmware and Cocoon as the gaming environment. No root, bootloader unlock, firmware replacement or security weakening is authorized. Root research is deferred because standalone Muse now works; revisit only with a demonstrated need, verified exact recovery image and separate approval.
- Three coherent environments: Cocoon gaming, everyday Android applications, and RotateMuse animated standby. Single-click hardware shortcut switches Cocoon/Android; swivel closes into Muse and opens back to the selected environment; full reboot defaults to Cocoon.
- Design for the 720×720 touchscreen and physical controls: a **jailbroken-iPhone-inspired** experience, combining familiar Files/Safari/iOS interaction patterns with user-controlled themes, layouts, widgets, animations and hardware customization. Follow the detailed design contract below. Original branding/assets; no claim to be iOS.
- Lightweight native Android implementation; minimize RAM, CPU, battery and background services. Offline-first where sensible; no unnecessary accounts, advertisements or Google service dependency. Preserve Android sandbox, lock security and normal emulator operation.
- Preserve installed application IDs, signing compatibility, settings, videos, saves and SD library. Never uninstall/clear data, auto-format, overwrite conflicting files, or publish private keys, device identifiers, ROMs or copyrighted assets.
- Separate user-reported physical acceptance, automated tests, compiled, installed, and independently verified results. Update this roadmap and relevant test/handoff records after every change.

## Owner-approved design direction — a jailbroken-iPhone-inspired experience

The target is **not stock iOS imitation**. The owner wants the familiar polish, navigation and visual language of an iPhone combined with the personalization freedom associated with a jailbroken iPhone, adapted to the RG Rotate. Android remains the underlying OS, Cocoon remains the default gaming environment, and RotateMuse remains the closed-device experience. **RotateOS** is a provisional umbrella name only, not an actual operating-system replacement or final branding decision.

### Design contract for every Rotate application

- Build a coherent premium visual system for the actual 720×720 touchscreen: original rounded-square icons, compact status information, translucent materials where performant, grouped settings, familiar bottom navigation, sheets, contextual menus, smooth transitions and consistent typography. Support both touch and controller focus/back navigation. No fake notch, wasted phone-shaped margins, clipping, or unnecessary scrolling.
- Offer a clean familiar default preset and optional more expressive jailbreak-style themes. Allow customization without forcing a particular color palette, icon grid, animation, or wallpaper. Include dark/light modes, reduced-motion and battery-friendly settings. Use original assets and do not copy Apple or third-party tweak branding.
- Design home/app organization around a customizable dock, icon layout/spacing, folders, wallpaper, widgets, optional hidden labels and app search. Any optional RotateHome shell belongs to the everyday Android side; it must not displace Cocoon as the boot gaming destination.
- Use a compact optional activity indicator inspired by Dynamic Island tweaks for media, downloads and supported background tasks in our own interfaces. Do not claim system-wide access to other apps' private state.
- Prefer native responsiveness over elaborate effects. Measure animation frame pacing, input latency, memory, thermal and battery impact on real hardware. Provide low-effects alternatives; never sacrifice Muse activation, sleep, emulator sessions or shortcut reliability for decoration.
- Jailbreak-inspired controls mean **configurable supported features**, not actual iOS, root, arbitrary code injection, disabling security, or bypassing Android permissions. Keep system-wide limitations explicit and offer supported in-app alternatives.

### P1/P2 — RotateTweaks and customization platform (new planned workstream)

After P0 is physically accepted, define a shared theme/preferences contract before building Files and Browse. Introduce a lightweight RotateTweaks manager as the customization capabilities become available; do not block the first two apps on implementing every tweak.

- [ ] **Theme engine (SnowBoard-inspired):** original icon packs, colors, wallpaper, accent palettes, appearance presets and previews; import/export documented SD-card theme packages, validate manifests/assets, apply only to supported Rotate surfaces and restore stock Rotate defaults.
- [ ] **Layout (Atria-inspired):** configurable icon grid, spacing, labels, dock and folders; test square-screen layouts, touch targets, controller navigation and large text.
- [ ] **Widgets (Xen HTML-inspired):** optional local clock/date, battery, media and gaming shortcuts; optional animated widgets with bounded resource use. Use declarative or bundled reviewed widget types, not arbitrary scripts or remote HTML with device privileges.
- [ ] **Animations (Cylinder-inspired):** selectable home transitions, folder opening, app entrance and optional launcher-reload presentation. Reduced motion, disable effects and safe fallback; a launcher reload is not an actual iOS respring.
- [ ] **Status/activity customization:** optional compact status-bar layouts, time/date, media/download progress and a Dynamic Island-inspired activity pill within supported surfaces. Accurate information only; no misleading system indicators.
- [ ] **Hardware actions (Activator-inspired):** supported configurable button/swivel actions, conflict detection, one action per press, reset to defaults and protected emergency/power behavior. Keep the owner-approved default F10 single-click Cocoon/Android switch and Cocoon boot destination; do not introduce competing handlers.
- [ ] **Control Center (CCSupport-inspired):** modular translucent quick controls and reordering for supported settings, media and shortcuts. If Android restricts direct changes, use clear system intents and report actual state.
- [ ] **Standby/clock (Designer-inspired):** reusable clock styles, position, typography and wallpaper presets integrated with Muse; preserve video/audio, correct orientation, dimming, countdown and genuine sleep.
- [ ] **Advanced file management (Filza-inspired):** integrate optional advanced details, archive inspection, safe batch operations and supported storage locations into RotateFiles; no unrestricted root filesystem access.
- [ ] **Storage maintenance (iCleaner-inspired):** show actual storage use, reviewable cleanup of our own caches and user-selected files, clear consequences and protected ROMs/saves/media; no silent deletion or indiscriminate system/app cache clearing.
- [ ] **App/theme catalog (Sileo-inspired):** browse installed Rotate apps and supported themes/tweaks, versions, changelogs, compatibility and updates. Reuse RotateUpdate for signed APKs and explicit install consent; declarative themes only initially. No arbitrary executable tweak repositories, code injection or untrusted package execution.
- [ ] **RotateTweaks UI:** searchable grouped settings for Appearance, Hardware & System, and Management; per-feature toggles, previews, applied state, compatibility and permission explanations. Unimplemented or unsupported features must be labeled as such, not fake switches.
- [ ] **Recovery and configuration:** local export/import, versioned schemas, transactional apply, last-known-good theme, accessible reset and safe-mode launch that disables optional customizations. Preserve application data and protect Cocoon/emulator access; do not describe this as Android system recovery.
- [ ] **Cross-app acceptance:** themes propagate consistently where supported; invalid/missing SD packages fail safely; settings survive restart; individual apps remain usable without RotateTweaks; disabling all tweaks restores a clean baseline. Test battery, latency, large text, controller focus, and hardware regression on real RG Rotate.

The named jailbreak tweaks are **interaction references only**, not dependencies, copied implementations or claims that iOS tweak packages will run. Exact visual presets, app icons and final umbrella branding are to be reviewed with the owner. The new work is additive and follows existing release gates.

## P0 — RotateMuse and hardware integration: immediate remaining tasks

Owner reports as of Nov 24 (latest local version to be established before work):
- [x] Swivel-close activation around 0.7 seconds in normal use; full video/audio and customization.
- [x] 720×720 video conversion (landscape and portrait with audio tested in v0.3.5).
- [x] Standalone accessibility-based operation without PC/manual Shizuku restart; cold reboot while physically closed launches Muse.
- [x] Normal swivel-open/close preserves selected Android or Cocoon environment in latest owner tests.
- [x] Existing countdown appearance and genuine display-off sleep via native power-button-equivalent action; preserve this working mechanism.
- [ ] **F10 single-click** replaces previous long-press requirement. Current long hold action waits for release and is unreliable in Cocoon and Android. Prefer initial key-down where supported; one action per press, suppress repeats, no competing hold handler; if firmware only provides release, document and minimize latency. Detect current environment rather than blind boolean toggling; maintain state across manual navigation and emulator launches. Test 10 successive switches and long-held button.
- [ ] **Closed-device shortcut:** investigate actual F10 delivery while closed and awake; currently does not appear to activate. If hardware permits, change underlying destination without disrupting Muse or waking intentional sleep; document hardware constraints. No false pass.
- [ ] **Boot defaults to Cocoon:** startup while open goes to Cocoon even if previously in Android. Startup while closed starts Muse and opening returns to Cocoon. Normal swivel cycles continue preserving current selected environment. Avoid duplicate launch/races and security bypass.
- [ ] **Boot orientation confirmed FAILED:** closed boot starts 90° counterclockwise and stays wrong or corrects too slowly. Determine whether firmware startup or Muse display/video/overlay orientation is responsible; synchronize before first visible frame where possible; no permanent offset that breaks normal swivel. Test boot open/closed and normal rotation.
- [ ] Regression: actual screen-off and audio stop, no wake loops, physical short power press, pocket protection, dim/countdown, multi-app foreground restoration (Cocoon, Android, PPSSPP, DuckStation, ordinary app), reboot disconnected from PC, orientation, video library and playback.
- [ ] Verify PPSSPP and DuckStation shortcuts on Cocoon home screen; existing emulator sessions remain intact.
- [ ] Stable personal release: automated tests/lint, actual signed APK(s), signature/upgrade compatibility, exact installed hash/version, in-place ADB upgrade only when authorized, retain APK in computer output and SD SetupPackages/RotateMuse; document physical results and unresolved items. Back up latest source privately; publish only reviewed source/assets and no keys. Longer-term battery/thermal and repeated reboot/swivel tests before public release.

## P1 — Shared Rotate design and application foundations

- [ ] Shared native UI components: square-aware spacing, touch targets, controller focus, search, context menus, sheets, navigation, typography, icons, light/dark, reduced-motion and accessibility options. Consistent settings and animations; no copied proprietary assets.
- [ ] Shared file-open/share contracts and safe local app-to-app integrations; avoid tightly coupling independent apps. Respect Android storage permissions and app sandbox.
- [ ] Establish per-app versioning, CI/test fixtures, APK signing and in-place upgrade/recovery policy. Signed update manifests, rollback planning (Android downgrade restrictions), user-controlled updates and release notes.
- [ ] Measure launch latency, memory/battery and rendering on actual hardware, especially alongside emulators. Avoid a large always-running shared service.

## P1 — RotateFiles (first new app)

- [ ] iPhone Files-inspired Browse, Recents, Favorites, search, grid/list, breadcrumbs, long-press menus, selection and batch actions.
- [ ] Internal shared storage, SD card, Downloads, ROMs, SetupPackages and RotateMuse media; correct permissions via SAF/shared-storage APIs, optional broader access only where justified. No root required.
- [ ] Copy/move/rename/create folders/share/open-with, safe recoverable deletion/Recently Deleted where supported; conflict resolution, free-space check, cancellation/resume and integrity verification.
- [ ] Transfer queue with actual speed, progress and ETA; protect active game data and original sources; strict duplicate review, no silent deletion.
- [ ] ZIP/7z inspection/extraction with traversal and archive-size protections; previews/Quick Look for supported files, media, ROM metadata and covers; per-console folder icons, emulator opening where supported.
- [ ] Optional Synology SMB/NAS locations, private credentials stored securely; offline local browsing remains functional.
- [ ] Test large SD libraries, removable media, failures, permission revocation, interrupted copies and square UI with touch/controller. Keep a standalone Android file manager; no automatic ROM conversion unless expressly selected.

## P1 — RotateBrowse (after Files)

- [ ] Lightweight Safari-inspired browser: bottom address/search bar, back/forward, share, bookmarks/favorites/start page, history, tabs and animated tab previews; full-screen, mobile/desktop modes, dark/light and controller navigation.
- [ ] WebView-based rendering initially, verify actual provider and security update availability; no root privileges, no unrestricted local-file access, no TLS-error bypass, safe external intents and download handling.
- [ ] Downloads with progress/cancel and explicit destination; hand off to RotateFiles safely; reader mode where feasible.
- [ ] Private browsing with genuinely isolated session storage/cookies where supported; clearly disclose limitations, never claim isolation without tests. Default browser registration is optional/user-controlled.
- [ ] Test sites, redirects, TLS failure, permissions, file upload/download, memory pressure, tab restoration and square screen. Never expose protected files or credentials through web content.

## P2 — Media and everyday apps (planned concepts, not implemented)

- [ ] RotatePhotos: familiar photo/video library, albums, search, previews, SD media, share and import to Muse; no unwanted duplication, privacy-respecting indexing.
- [ ] RotateMusic: lightweight offline audio library, playlists, playback controls, audio focus, background/media session, sleep timer and SD storage.
- [ ] RotateControl: iPhone-inspired quick settings for supported brightness, volume, Wi-Fi/Bluetooth state, battery and shortcuts; use supported intents/settings when direct controls restricted; no overlays that compromise security.
- [ ] RotateSettings: cohesive app-suite preferences, permissions, appearance, storage, diagnostics, shortcuts, accessibility and reset/backup controls; distinguish system settings from app settings.
- [ ] RotateHome: optional iPhone-inspired home/app organization, dock, original icons, folders, search and animations; Cocoon remains default gaming destination, no forced launcher replacement.
- [ ] RotateLock: optional lock/standby presentation within Android security constraints, never replace or bypass secure authentication; evaluate overlap with Muse.
- [ ] RotateBoot: optional boot presentation research only; no firmware/system modification without separate explicit approval.
- [ ] RotateBackup: export/import supported app settings, media references, emulator configurations and saves where permitted; encrypted/private backup where appropriate, validate restores, no blanket root access.
- [ ] RotateUpdate: unified signed APK update manager, local/SD packages and trusted release sources, signature checks and explicit install consent.
- [ ] Optional calculator and downloads UI as later convenience features; prioritize core reliability over feature creep.

## P2 — Gaming AI companion (coordinate with existing Gaming-AI repository and issue #7)

- [ ] Compare built-in Anbernic AI before duplicating it; voice-first consistent personality, natural conversation, game-specific learning/adaptation, session and long-term memory on SD, optional temporary screenshot awareness.
- [ ] Offline-capable voice where feasible; avoid Piper and complicated chained speech pipelines; unobtrusive grayscale orb, touch/controller friendly premium 720×720 UI, privacy controls and opt-in screenshot access.
- [ ] Preserve 8 GiB companion budget (not preallocated), 8 GiB free safety reserve and optional NAS backup; ensure gaming performance and battery are unaffected. Windows build/signing automation and actual APK acceptance.

## Parallel work — Retro Library Studio / library and device setup

- [ ] Reconcile newest local preparation results with existing [roadmap](ROADMAP.md) and [verification matrix](VERIFICATION_MATRIX.md); last research handoff reported 239/249 copied and verified, 10 needing repair; current state must be rechecked, not assumed.
- [ ] Repair failed conversions individually without touching good outputs, retain originals; batch PS1/PSP PSN imports, supported 7z workflows, clear per-game/per-disc stages and reliable Stop/resume; exact console-scoped duplicate detection and conservative artwork.
- [ ] PS1 CHD per disc and ordered M3U per game; one parent folder and one logical cover; real emulator disc swapping, save retention and Clock Tower II actual source compatibility remain evidence-gated.
- [ ] Complete physical card capacity/exFAT/adapter checks, safe verified transfers, no automatic format; do not transfer while relevant emulator is actively using target files.
- [ ] PSP/PS1/DS targets plus select PS2/GameCube only after actual performance testing; GBC/GBA limited to USA Pokémon and explicitly agreed games, not indiscriminate full libraries. Confirm Cocoon indexing, covers, favorites, emulator mappings and standalone shortcuts.
- [ ] Preserve Windows companion Gallery/List, compact cards and readable details, 125% UI scaling, actual card vs virtual capacity distinction, NAS workflow and recovery.

## P3 — Deferred platform exploration

- [ ] Root feasibility: read-only research only if needed; exact firmware, locked bootloader, recovery PAC provenance and rollback readiness must be proven before any separate approval. No SPL/FDL/U-Boot experiments, no disabling SELinux/AVB or lock security. GammaOS comparison is research only, not a decision to install.
- [ ] Public release readiness: original assets, onboarding, clear accessibility permission explanation, privacy disclosures, install/uninstall and rollback instructions, firmware/launcher compatibility, actual battery benchmarks, reproducible build and user-tested setup. No claims of universal compatibility or superiority without evidence.

## Codex continuation rule

Read this document plus existing local project notes and latest code before editing. Immediate priorities are the three P0 fixes (single-click shortcut including closed-state investigation, Cocoon on reboot, boot orientation). Sleep and standalone reboot recovery are working; regression-test, do not redesign. Once P0 passes, stabilize and back up, establish the shared jailbreak-inspired design/theme contract, then build Files and Browse in that order. Introduce RotateTweaks incrementally alongside supported customization features. Treat later concepts as backlog, not permission to implement them all at once. Update roadmap at each milestone and preserve old evidence. Do not stop an authorized implementation at a source ZIP if a real signed APK can be built and verified.
