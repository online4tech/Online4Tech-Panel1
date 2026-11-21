# Online4Tech Panel — Source Registry

## Scope
This registry documents the direct download URLs referenced by `o4t_database.json`. The database now stores `source_url`, `source_host`, `source_type`, `source_attribution`, and `mirror_status` on each downloadable item.

## Hosting policy
- Scripts and packages already hosted under `online4tech/Online4Tech-Panel1` remain hosted by Online4Tech.
- Third-party URLs are preserved verbatim and listed in `sources/source-manifest.json`.
- Third-party files are **not copied into this repository** until the original author/license or explicit redistribution permission is verified. This avoids stripping attribution or redistributing code/packages without permission.
- An Online4Tech-hosted installer may still fetch a third-party payload internally. The direct command registry does not prove that every nested download inside every shell script has been mirrored; those nested references require a separate script-by-script content review.

## Safety changes
- The 104 entries that referenced `scripts/main_installer.sh` are quarantined. That legacy script downloads and extracts the Klll-Pro skin regardless of the selected entry.
- The legacy shared installer now fails closed.
- Four feed removal commands that used broad wildcard deletion have been disabled. Pure2 feed removal is scoped to `/etc/opkg/external-extra-feed.conf`.
- The store refuses to run entries marked `enabled: false`.

## Review limitations
This is a static review of database command strings and removal commands. It does not execute scripts, download all remote payloads, verify signatures/checksums, or certify compatibility with any Enigma2 image. HTTP links, TLS verification bypasses, and remote shell execution are recorded in the audit report and still require remediation after endpoint and package verification.

See:
- `reports/command-audit-2026-11.json`
- `sources/source-manifest.json`
