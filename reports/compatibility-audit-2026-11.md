# Online4Tech Panel — Compatibility & Preservation Audit

**Audit date:** 2026-11-21  
**Working branch:** `maintenance/audit-sources-2026-11`  
**Production branch:** `main` (not modified)

## Preservation commitment

This maintenance pass is additive and conservative:
- No repository file paths are intentionally removed.
- The original top-level `plugin/` directory is retained; the 7.5 package builder now uses the authoritative installed plugin source tree instead.
- All existing database entries remain present. The 58 entries that still point to the shared, incorrect installer retain their original command text in `legacy_cmd`; they are paused rather than deleted or silently redirected. Klll-Pro-FHD was restored separately through an item-specific Online4Tech wrapper that credits Biko-73 and leaves the original payload upstream.
- Online4Tech names, branding assets, category icons, logo, and UI styling are retained.

## Repository inventory reviewed

- 825 tracked file entries in the production tree.
- 824 database item records with install/removal commands in the static command audit.
- 386 shell scripts under `scripts/`.
- 69 tracked entries under the installed plugin directory, including three Python cache files.
- The installed plugin tree contains the main Python entry points, the 7.5 store implementation, Online4Tech logo/plugin icons, and the category/UI icon set.
- The repository contains a 7.5 IPK and DEB artifact (386,586 bytes each, same Git blob) and an older 7.0 IPK artifact (8,718 bytes).

## Issues found and addressed on this branch

### 1. IPK builder was building the wrong source/version

The previous `build_ipk.py` built version 7.0 from the legacy top-level `plugin/` directory and only added a small subset of files. That did not match the current 7.5 installed plugin tree.

The builder now:
- Targets `usr/lib/enigma2/python/Plugins/Extensions/Online4Tech/`.
- Packages the complete source and asset tree recursively.
- Excludes only Python bytecode/cache files.
- Requires the core entry points, plugin icon, and Online4Tech logo.
- Refuses to build if fewer than 60 real plugin files are found.
- Uses version 7.5 and the matching package filename.
- No longer has package scripts that recursively delete the whole plugin directory.

**Validation status:** GitHub Actions run 44891276787 successfully executed the builder against a complete checkout. The existing 7.5 IPK and DEB each contained 69 archive entries and included the plugin entry point, store, plugin icon, and Online4Tech logo. The corrected builder generated both IPK and DEB packages with 66 real source/asset files (excluding three Python cache files), and both generated archives passed structural checks.

### 2. Installer safety and consistency

The canonical `install.sh` now:
- Uses normal HTTPS certificate validation (no `--no-check-certificate` / `curl -k`).
- Validates that the download is an ar archive before installation.
- Uses the detected package manager without force-overwrite.
- Does not delete the receiver's database cache.
- Does not recursively chmod the plugin directory.
- Avoids `killall -9 enigma2` and uses a graceful service/init restart path.

The legacy `install_panel.sh` entry point now delegates to the canonical installer over verified HTTPS instead of downloading only three Python files and omitting the branding/category assets.

### 3. Store database connection and paused-item presentation

The 7.5 store implementation now:
- Uses the default verified TLS context.
- Validates the downloaded JSON before replacing the cache.
- Writes through a temporary cache file and preserves the last working cache if a refresh fails.
- Clearly labels paused entries in the details pane and states that the entries are retained.

## Important outstanding work — no items have been deleted

### 58 entries still need verified, item-specific installers

The old shared `scripts/main_installer.sh` always downloads and extracts the Klll-Pro skin, regardless of the selected item. The 59 records that still reference it remain visible in the database but their install action is paused. Their previous command is retained as `legacy_cmd` for traceability.

These entries must be mapped one by one to a verified, item-specific script or package before their install action is restored. A similarly named script is not sufficient proof.

Examples found during review:
- The KeyAdder upstream installer deletes existing `AddKey`, `KeyAdder`, and `Biscotto` directories and performs broad temporary-file cleanup. It is not safe to reactivate as-is.
- The Levi45 emulator installer removes an existing plugin directory and force-restarts Enigma2. It needs a separate safety review before being mapped to any database item.
- Some other candidate scripts use disabled TLS verification or broad cleanup commands.

Restored entries now include Klll-Pro-FHD, KeyAdder, Levi45 Emulator, EPGImport-99, 39 Ciefp-family plugins, and Abertis Auto Switcher PRO (pinned v1.9.24 package). Their Online4Tech wrappers use verified HTTPS, validate downloads, avoid pre-deleting existing plugin directories, and retain the original authors' attribution. EPGImport is explicitly IPK/opkg-only. CiefpYouTube and CiefpRottenTomatoes remain paused because their installers require additional binaries/dependencies that need separate review. No guessed command has been substituted for the remaining items.

## Testing still required

- Complete: CI now builds both 7.5 packages from the full repository checkout and verifies their archive members and required branding/plugin files.
- Install and upgrade on representative Enigma2 images (OpenATV, OpenPLi, DreamOS, and other images explicitly supported by the project).
- Verify plugin menu registration, category browsing, icon/logo rendering, preferences, database refresh, install/remove actions, and restart behavior.
- Verify package removal leaves user-created/unowned files untouched.
- Test each restored third-party installer individually and preserve original author attribution.

**No live receiver commands were executed during this audit. CI confirms source syntax and package structure, not runtime behavior on a real Enigma2 receiver. Individual plugin payloads and receiver-specific behavior still require device testing.**

### First-party source files requiring recovery

The expanded source-file check found two URLs still used by active database commands whose target files are absent from both `main` and the maintenance branch:

- `install_o4t_emu.sh` — Online4Tech Web Panel installer.
- `scripts/channel-romeh_installer.sh` — Ahmed Romeh Channels installer.

Both database entries remain present and enabled. No replacement or guessed installer was substituted, and neither item was disabled. The original source files must be restored before these two actions can be considered operational.

## Expanded command and source checks — 2026-11-21

- The database contains **824** records: **766 active** and **58 retained in quarantine**. No records were deleted.
- CI checks the shell syntax of every non-empty `cmd`, `remove_cmd`, and preserved `legacy_cmd` string; the latest completed check passed **1,323 command strings** across all 824 records.
- CI also syntax-checks every `*.sh` file under `scripts/`.
- The active command set still contains **69 HTTP command records**, **87 commands that bypass TLS certificate verification**, and **755 commands that pipe downloaded scripts directly to `/bin/sh`**. These were not silently rewritten because HTTP-to-HTTPS support and older receiver TLS compatibility must be verified per source/image.
- **302 third-party sources** remain external pending rights and integrity review. Their presence is preserved; they are not represented as verified.
- The first-party source check found **354 present, non-empty source files** and two explicitly tracked missing source files: `install_o4t_emu.sh` and `scripts/channel-romeh_installer.sh`. Their database entries remain enabled; no guessed replacement or disablement was applied.

These checks validate syntax, repository paths, and package structure. They do not execute arbitrary installers or prove runtime compatibility on a physical receiver.


## First isolated recovery batch — Abertis Auto Switcher PRO

- Restored the Abertis Auto Switcher entry through `scripts/install_abertis_auto_switcher.sh`.
- Pinned the upstream release to v1.9.24 and embedded the official SHA-256 digests for both IPK and DEB assets.
- The wrapper validates the downloaded package before installation and uses `opkg install` or `dpkg -i` without force-overwrite.
- Removal uses the package manager rather than recursively deleting the plugin directory.
- The wrapper does not disable TLS verification or automatically restart Enigma2.
- 58 other quarantined entries remain untouched pending their own source and installer review.
- CI syntax and database validation must pass; physical receiver install/upgrade/remove testing is still required.
