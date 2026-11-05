# Experimental macOS bundle

This directory builds one Fusion `.bundle` containing native dependency sets
for Fusion's CPython 3.14 runtime on Apple Silicon and Intel Macs. The build can
run on Windows because pip is given explicit foreign platform and ABI tags.

From the repository root:

```powershell
python setup/macos/build_bundle.py 1.1.0
```

The output is `dist/AirfoilSplines-1.1.0-macOS-universal.zip`. It contains:

```text
AirfoilSplines.bundle/
  PackageContents.xml
  Contents/
    AirfoilSplines.py
    AirfoilSplines.manifest
    _vendor/
    lib/
      macos-cp314-arm64/
      macos-cp314-x86_64/
```

The build downloads only binary NumPy and SciPy wheels and fails if a matching
wheel is unavailable. It cannot execute macOS native extensions on a Windows
host, so the resulting archive still requires an import and Fusion smoke test
on both Mac architectures before release.

For manual testing, extract `AirfoilSplines.bundle` into Fusion's per-user
Application Plugins directory, restart Fusion, and enable the add-in. Keep this
experimental bundle private until both architectures have been tested.
