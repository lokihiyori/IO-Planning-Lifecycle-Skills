from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "check_io_flow_updates.py"
SPEC = importlib.util.spec_from_file_location("check_io_flow_updates", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class UpdateCheckerTests(unittest.TestCase):
    def test_change_summary_reports_versions_ids_and_diff(self) -> None:
        previous = {
            "last_commit_sha": "a" * 40,
            "last_blob_sha": "b" * 40,
            "last_version": "0.1.0",
        }
        current = MODULE.Snapshot(
            commit_sha="c" * 40,
            blob_sha="d" * 40,
            version="0.2.0",
            author="teammate",
            timestamp="2026-09-01T12:00:00Z",
            message="Update EP-02 Type B",
            commit_url="https://github.com/example/repo/commit/" + "c" * 40,
            content='version: "0.2.0"\n### EP-02\n#### Type B\n| OD-03 | resolved |\n',
        )
        result = MODULE.build_change(
            "example/repo",
            "flow.md",
            previous,
            current,
            'version: "0.1.0"\n### EP-02\n#### Type A\n| OD-03 | open |\n',
        )

        self.assertEqual(result["status"], "changed")
        self.assertEqual(result["previous_version"], "0.1.0")
        self.assertEqual(result["current_version"], "0.2.0")
        self.assertEqual(result["affected_ids"], ["EP-02", "OD-03", "Type A", "Type B"])
        self.assertIn('-version: "0.1.0"', result["diff"])
        self.assertIn('+version: "0.2.0"', result["diff"])

    def test_state_round_trip_records_remote_baseline(self) -> None:
        snapshot = MODULE.Snapshot(
            commit_sha="1" * 40,
            blob_sha="2" * 40,
            version="1.2.3",
            author="owner",
            timestamp="2026-09-01T12:00:00Z",
            message="Baseline",
            commit_url="https://github.com/example/repo/commit/" + "1" * 40,
            content="version: 1.2.3\n",
        )
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "state.json"
            MODULE.save_state(state_path, "example/repo", "flow.md", "main", snapshot)
            state = MODULE.load_state(state_path)

        assert state is not None
        self.assertEqual(state["last_commit_sha"], snapshot.commit_sha)
        self.assertEqual(state["last_blob_sha"], snapshot.blob_sha)
        self.assertEqual(state["last_version"], "1.2.3")

    def test_default_state_path_is_local_and_stable(self) -> None:
        path = MODULE.default_state_file("example/repo", "examples/io flow.md")
        self.assertEqual(path.parent, Path(".io-flow-sync"))
        self.assertEqual(path.suffix, ".json")
        self.assertNotIn(" ", path.name)


if __name__ == "__main__":
    unittest.main()
