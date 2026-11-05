import os
import tempfile
import unittest

from utils.dependency_paths import bundled_dependency_dir


class DependencyPathTests(unittest.TestCase):
    def test_non_macos_uses_legacy_lib_directory(self):
        self.assertEqual(
            bundled_dependency_dir(
                "/add-in", sys_platform="win32", machine="AMD64", version_info=(3, 14)
            ),
            os.path.join("/add-in", "lib"),
        )

    def test_macos_selects_matching_bundled_directory(self):
        with tempfile.TemporaryDirectory() as addin_dir:
            expected = os.path.join(addin_dir, "lib", "macos-cp314-arm64")
            os.makedirs(expected)
            self.assertEqual(
                bundled_dependency_dir(
                    addin_dir,
                    sys_platform="darwin",
                    machine="arm64",
                    version_info=(3, 14),
                ),
                expected,
            )

    def test_macos_normalizes_intel_architecture_name(self):
        with tempfile.TemporaryDirectory() as addin_dir:
            expected = os.path.join(addin_dir, "lib", "macos-cp314-x86_64")
            os.makedirs(expected)
            self.assertEqual(
                bundled_dependency_dir(
                    addin_dir,
                    sys_platform="darwin",
                    machine="AMD64",
                    version_info=(3, 14),
                ),
                expected,
            )

    def test_macos_falls_back_for_local_dependency_installations(self):
        with tempfile.TemporaryDirectory() as addin_dir:
            self.assertEqual(
                bundled_dependency_dir(
                    addin_dir,
                    sys_platform="darwin",
                    machine="arm64",
                    version_info=(3, 15),
                ),
                os.path.join(addin_dir, "lib"),
            )


if __name__ == "__main__":
    unittest.main()
