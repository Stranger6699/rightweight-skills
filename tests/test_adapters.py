from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class AdapterTests(unittest.TestCase):
    def test_all_install_manifests_are_valid_json(self) -> None:
        for relative in (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
            ".cursor-plugin/plugin.json",
            "gemini-extension.json",
            "package.json",
        ):
            with self.subTest(relative=relative):
                document = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertEqual(document["name"], "rightweight-skills")
                self.assertTrue(document.get("version"))

    def test_each_adapter_points_at_bootstrap_and_mapping(self) -> None:
        bootstrap = (ROOT / "skills/using-rightweight/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("RIGHTWEIGHT-BOOTSTRAP", bootstrap)
        for harness in ("claude", "cursor", "codex", "gemini", "opencode", "pi", "copilot"):
            mapping = ROOT / "skills/using-rightweight" / "references" / f"{harness}-tools.md"
            self.assertTrue(mapping.is_file(), harness)
            self.assertGreater(len(mapping.read_text(encoding="utf-8")), 100)

    def test_hooks_and_runtime_plugins_use_the_bootstrap(self) -> None:
        for relative in (
            "hooks/session-start",
            ".opencode/plugins/rightweight.js",
            ".pi/extensions/rightweight.ts",
        ):
            with self.subTest(relative=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn("using-rightweight", content)

    def test_session_start_hook_emits_sdk_context_json(self) -> None:
        shell = "bash"
        if os.name == "nt":
            candidates = [
                Path(r"C:\Program Files\Git\bin\bash.exe"),
                Path(r"C:\Program Files (x86)\Git\bin\bash.exe"),
            ]
            git = shutil.which("git")
            if git:
                exec_path = subprocess.run(
                    [git, "--exec-path"], capture_output=True, text=True, check=True
                ).stdout.strip()
                candidates.append(Path(exec_path).parents[2] / "bin" / "bash.exe")
            found = next((candidate for candidate in candidates if candidate.is_file()), None)
            if found is None:
                self.skipTest("Git Bash is not installed")
            shell = str(found)
        result = subprocess.run(
            [shell, str(ROOT / "hooks/session-start")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        document = json.loads(result.stdout)
        self.assertIn("additionalContext", document)
        self.assertIn("RIGHTWEIGHT-BOOTSTRAP", document["additionalContext"])
        self.assertIn("Codex tool mapping", document["additionalContext"])

    def test_third_party_notice_covers_superpowers_adaptations(self) -> None:
        notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        for relative in (
            "hooks/session-start",
            "hooks/run-hook.cmd",
            ".opencode/plugins/rightweight.js",
            ".pi/extensions/rightweight.ts",
        ):
            self.assertIn(f"`{relative}`", notice)
        self.assertIn("Copyright (c) 2025 Jesse Vincent", notice)
        self.assertIn("MIT License", notice)


if __name__ == "__main__":
    unittest.main()
