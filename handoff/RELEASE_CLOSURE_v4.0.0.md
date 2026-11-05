# v4.0.0 release closure — verified 2026-11-05

**Status: BLOCKED — not a completed GitHub Release.** This is retrospective release evidence, not a new version or authorization for production integration.

## Immutable source and CI provenance
- v4.0.0 merged release commit candidate: `3afc90d4f4bb3657acf86a523ae369adbf943f5b`. Confirm it is the correct historical source tree before tagging; do not tag current main (currently `09b36802246d907079030130aee020c16aa55ebe`, which already includes later releases).
- PR #58: https://github.com/tradoanson/Core_AI_Tra_Son/pull/58
- v4.0.0 main CI run: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41476142102
- Post-handoff-merge v4.0.0 workflow on main: https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41757245778 — six jobs succeeded: Python 3.11/3.12/3.13, Windows native locking, Windows viewer EXE, wheel.
- Handoff PR #69: https://github.com/tradoanson/Core_AI_Tra_Son/pull/69 (merged at `09b36802246d907079030130aee020c16aa55ebe`).

## Existing CI artifacts (not yet release assets)
Artifacts of original run 41476142102, confirmed non-expired on 2026-11-05:
- `core-ai-tra-son-wheel-v4.0.0`, artifact ID `13158540562`, ZIP size 56,533 bytes.
- `core-ai-tra-son-windows-exe-v4.0.0`, artifact ID `13158225825`, ZIP size 11,139,804 bytes.

A second main run 41757245778 generated artifact IDs `13289235367` (wheel, 56,532 bytes) and `13288423011` (Windows EXE, 11,138,551 bytes). **Do not assume these archives are byte-identical**: sizes differ, and no SHA256 has been independently verified. Use one selected, source-provenance-matched build set; document which one.

## Maintainer-only release closure
1. Confirm release commit `3afc90d4f4bb3657acf86a523ae369adbf943f5b` corresponds to the audited v4.0.0 source and selected artifact run. Rebuild from that commit if provenance is uncertain.
2. Download selected artifact ZIPs via GitHub Actions. Compute SHA256 locally with `Get-FileHash -Algorithm SHA256 <path>` (Windows) or `sha256sum <path>` (Linux); record hashes, sizes, and source run ID in the release notes.
3. Create annotated tag **at that historical commit**, never current main: `git tag -a v4.0.0 3afc90d4f4bb3657acf86a523ae369adbf943f5b -m "Core AI Tra Son v4.0.0"`; verify with `git rev-parse v4.0.0^{}`; push tag after confirmation.
4. Publish GitHub Release `v4.0.0` targeting the verified tag. Attach the selected verified wheel and Windows EXE artifacts and SHA256 manifest; do not mislabel later main builds as original v4.0.0 binaries.
5. Verify GitHub tag and Release API, release asset checksums, PR #58, main CI, backward compatibility and independent-core test evidence. Only then mark handoff complete.

## Explicit restrictions
No live Auto VTND / Web integration, no real data, no changes to Core Engine, GUI coupling or backward compatibility, and no further version development. GitHub connector in this run can read tags/releases and write repository files/PRs but cannot create tags or Releases. This checklist does **not** claim that those operations occurred.
