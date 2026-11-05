"""Build a dual-architecture macOS Fusion bundle on any host platform."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SETUP_DIR = Path(__file__).resolve().parent
DEFAULT_CORE = ROOT.parent / "airfoil-splines-core"
MAC_TARGETS = {
    "arm64": "macosx_14_0_arm64",
    "x86_64": "macosx_14_0_x86_64",
}


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def copy_sources(destination: Path) -> None:
    sys.path.insert(0, str(ROOT / "setup"))
    try:
        from stage_for_build import copy_to_staging
    finally:
        sys.path.pop(0)
    if not copy_to_staging(str(ROOT), str(destination)):
        raise RuntimeError("Could not stage the add-in sources.")


def write_version_files(bundle: Path, contents: Path, version: str) -> None:
    manifest_path = contents / "AirfoilSplines.manifest"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["version"] = version
    manifest_path.write_text(json.dumps(manifest, indent="\t") + "\n", encoding="utf-8")

    package_tree = ET.parse(SETUP_DIR / "PackageContents.xml")
    package_tree.getroot().set("AppVersion", version)
    ET.indent(package_tree, space="    ")
    package_tree.write(bundle / "PackageContents.xml", encoding="utf-8", xml_declaration=True)


def install_core(contents: Path, core: Path) -> None:
    if not (core / "pyproject.toml").is_file():
        raise RuntimeError(f"Local airfoil-splines-core project not found: {core}")
    run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-compile",
        "--no-deps",
        "--target",
        str(contents / "_vendor"),
        str(core),
    ])


def install_native_dependencies(contents: Path, architecture: str, platform_tag: str) -> None:
    target = contents / "lib" / f"macos-cp314-{architecture}"
    run([
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-compile",
        "--only-binary=:all:",
        "--implementation=cp",
        "--python-version=3.14",
        "--abi=cp314",
        f"--platform={platform_tag}",
        "--target",
        str(target),
        "--requirement",
        str(SETUP_DIR / "requirements-cp314.txt"),
    ])


def clean_generated_files(contents: Path) -> None:
    for path in sorted(contents.rglob("__pycache__"), reverse=True):
        shutil.rmtree(path)
    for pattern in ("*.pyc", "*.pyo", "*.pyd"):
        for path in contents.rglob(pattern):
            path.unlink()


def verify_bundle(bundle: Path, contents: Path) -> None:
    required = [
        bundle / "PackageContents.xml",
        contents / "AirfoilSplines.py",
        contents / "AirfoilSplines.manifest",
        contents / "_vendor" / "airfoil_splines_core" / "__init__.py",
    ]
    required.extend(
        contents / "lib" / f"macos-cp314-{architecture}" / package / "__init__.py"
        for architecture in MAC_TARGETS
        for package in ("numpy", "scipy")
    )
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError("Bundle verification failed; missing:\n" + "\n".join(missing))

    native_extensions = list((contents / "lib").rglob("*.so"))
    if not native_extensions:
        raise RuntimeError("Bundle verification failed; no macOS native extensions were found.")
    if list(contents.rglob("*.pyd")):
        raise RuntimeError("Bundle verification failed; Windows extensions are present.")


def create_zip(bundle: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(bundle.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(bundle.parent))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="Release version written into the bundle metadata")
    parser.add_argument("--core", type=Path, default=DEFAULT_CORE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    output = args.output or ROOT / "dist" / f"AirfoilSplines-{args.version}-macOS-universal.zip"
    output = output.resolve()
    with tempfile.TemporaryDirectory(prefix="airfoil-splines-macos-") as temp_dir:
        bundle = Path(temp_dir) / "AirfoilSplines.bundle"
        contents = bundle / "Contents"
        copy_sources(contents)
        write_version_files(bundle, contents, args.version)
        install_core(contents, args.core.resolve())
        for architecture, platform_tag in MAC_TARGETS.items():
            install_native_dependencies(contents, architecture, platform_tag)
        clean_generated_files(contents)
        verify_bundle(bundle, contents)
        create_zip(bundle, output)

    print(f"Built {output}")


if __name__ == "__main__":
    main()
