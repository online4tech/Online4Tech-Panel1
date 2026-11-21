#!/bin/sh
# Online4Tech safety hold — 2026-11-21
#
# This legacy entry point was incorrectly referenced by 104 unrelated store
# entries. It downloads and extracts the Klll-Pro skin, regardless of the
# selected item. Execution is intentionally blocked until every affected
# database entry has a verified, item-specific installer and source attribution.

echo "[Online4Tech] BLOCKED: legacy shared installer is quarantined."
echo "[Online4Tech] It previously installed Klll-Pro for unrelated entries."
echo "[Online4Tech] Please use the corrected store database after item review."
exit 1
