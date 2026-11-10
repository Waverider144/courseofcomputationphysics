"""Check portable hardware records and remote workspace boundaries."""
import importlib.util
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT/"Vol0_Linear_Algebra_HPC/code_examples/run_accelerators.py"
SPEC = importlib.util.spec_from_file_location("accelerator_runner", RUNNER)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicationTests(unittest.TestCase):
    def test_record_anonymization_preserves_measurements(self):
        source = Path("/private/course")
        workspace = source/"experiment"
        report = {"remote": True, "host": socket.gethostname(), "workspace": str(workspace),
                  "commands": [{"command": [str(source/"code.cpp"), str(workspace/"build/executable")],
                                "stderr": f"{socket.gethostname()}: {workspace}/cache"}],
                  "measurements": [{"seconds": 1.234567890123e-6, "error": 3e-16}],
                  "status": None}
        public = MODULE.portable_record(report, workspace, source)
        self.assertEqual(public["host"], "remote")
        self.assertEqual(public["workspace"], "<WORKSPACE>")
        self.assertEqual(public["commands"][0]["command"],
                         ["<SOURCE>/code.cpp", "<WORKSPACE>/build/executable"])
        self.assertEqual(public["measurements"], report["measurements"])
        self.assertIsNone(public["status"])
        self.assertEqual(report["workspace"], str(workspace))

    def test_remote_requires_explicit_boundaries(self):
        result = subprocess.run([sys.executable, str(RUNNER), "--remote"],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--workspace and --allowed-root", result.stderr)

    def check_rejected_workspace(self, workspace, root):
        result = subprocess.run([sys.executable, str(RUNNER), "--remote",
                                 "--workspace", str(workspace), "--allowed-root", str(root)],
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be a child", result.stderr)
        self.assertFalse((workspace/"build").exists())

    def test_outside_and_root_workspaces_are_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/"allowed"
            root.mkdir()
            self.check_rejected_workspace(Path(tmp)/"outside", root)
            self.check_rejected_workspace(root, root)

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, outside = base/"allowed", base/"outside"
            root.mkdir()
            outside.mkdir()
            link = root/"link"
            link.symlink_to(outside, target_is_directory=True)
            self.check_rejected_workspace(link/"experiment", root)


if __name__ == "__main__":
    unittest.main()
