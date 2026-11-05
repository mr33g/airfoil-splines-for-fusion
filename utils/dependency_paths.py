"""Resolve add-in-local dependency directories for the active runtime."""

from __future__ import annotations

import os
import platform
import sys


def bundled_dependency_dir(
    addin_dir: str,
    *,
    sys_platform: str | None = None,
    machine: str | None = None,
    version_info: tuple[int, int] | None = None,
) -> str:
    """Return the best dependency directory for the current Python runtime.

    macOS release bundles may contain more than one native dependency set.
    Keep the traditional ``lib`` directory as a fallback so existing local
    installations and the Windows installer continue to work unchanged.
    """
    lib_dir = os.path.join(addin_dir, "lib")
    active_platform = sys_platform if sys_platform is not None else sys.platform
    if active_platform != "darwin":
        return lib_dir

    active_machine = (machine if machine is not None else platform.machine()).lower()
    architecture = {
        "aarch64": "arm64",
        "arm64": "arm64",
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
    }.get(active_machine, active_machine)
    major, minor = version_info if version_info is not None else sys.version_info[:2]
    candidate = os.path.join(lib_dir, f"macos-cp{major}{minor}-{architecture}")
    return candidate if os.path.isdir(candidate) else lib_dir
