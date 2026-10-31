"""v2.0.0 offline stable SHADOW acceptance manifest.

This is a deterministic policy gate over caller-supplied CI evidence, NOT a
GitHub API client or production approval.
"""
from dataclasses import dataclass

REQUIRED_JOBS=("python-3.11","python-3.12","python-3.13","windows-native","wheel-sha256","versioned-verification")

@dataclass(frozen=True)
class StableShadowVerdict:
    status: str
    missing: tuple[str,...]
    failed: tuple[str,...]
    action_executed: bool = False
    production_approved: bool = False

def assess_stable_shadow(jobs, *, tests_discovered, expected_version="2.0.0",
                         package_version="2.0.0", shadow_boundary=True):
    if type(jobs) is not dict or any(type(k) is not str or type(v) is not bool for k,v in jobs.items()):
        raise ValueError("job evidence must be a string-to-bool map")
    if type(tests_discovered) is not int or tests_discovered < 0:
        raise ValueError("invalid test count")
    if type(expected_version) is not str or type(package_version) is not str:
        raise ValueError("invalid versions")
    missing=tuple(k for k in REQUIRED_JOBS if k not in jobs)
    failed=tuple(k for k in REQUIRED_JOBS if jobs.get(k) is False)
    if tests_discovered < 407:
        failed+=("test_count",)
    if expected_version != "2.0.0" or package_version != expected_version:
        failed+=("version_mismatch",)
    if shadow_boundary is not True:
        failed+=("shadow_boundary",)
    return StableShadowVerdict("PASS" if not missing and not failed else "BLOCKED",missing,failed)
