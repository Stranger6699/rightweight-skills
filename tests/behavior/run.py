#!/usr/bin/env python3
"""Run isolated, trace-based behavior scenarios against Codex CLI."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[2]
SCENARIOS_PATH = Path(__file__).with_name("scenarios.json")


@dataclass
class Action:
    index: int
    kind: str
    text: str
    paths: tuple[str, ...] = ()
    exit_code: int | None = None


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def fixture_diagnose_only(workdir: Path) -> None:
    write(
        workdir / "src" / "login.py",
        """attempts = 0


def login(username: str, password: str) -> bool:
    global attempts
    attempts += 1
    return username == "demo" and password == "secret" and attempts % 2 == 0
""",
    )
    write(
        workdir / "tests" / "test_login.py",
        """import unittest

from src.login import login


class LoginTests(unittest.TestCase):
    def test_valid_credentials_are_stable(self):
        self.assertTrue(login("demo", "secret"))
        self.assertTrue(login("demo", "secret"))


if __name__ == "__main__":
    unittest.main()
""",
    )


def fixture_plan_only(workdir: Path) -> None:
    write(
        workdir / "README.md",
        """# Cache Service

The service currently stores JSON cache entries in `data/cache-v1/`.
The requested migration must preserve reads during a rolling deployment.
""",
    )
    write(workdir / "src" / "cache.py", "CACHE_VERSION = 1\n")
    write(workdir / "tests" / "test_cache.py", "def test_placeholder():\n    assert True\n")


def fixture_tdd_email(workdir: Path) -> None:
    write(
        workdir / "src" / "email_validator.py",
        """def validate_email(value: str) -> bool:
    raise NotImplementedError
""",
    )
    write(workdir / "tests" / "__init__.py", "")


def fixture_verify_pressure(workdir: Path) -> None:
    write(
        workdir / "src" / "slugify.py",
        """def slugify(value: str) -> str:
    return value.lower().replace(" ", "_")
""",
    )
    write(
        workdir / "tests" / "test_slugify.py",
        """import unittest

from src.slugify import slugify


class SlugifyTests(unittest.TestCase):
    def test_words_use_hyphens(self):
        self.assertEqual(slugify("Hello World"), "hello-world")


if __name__ == "__main__":
    unittest.main()
""",
    )


FIXTURES: dict[str, Callable[[Path], None]] = {
    "diagnose-only": fixture_diagnose_only,
    "plan-only": fixture_plan_only,
    "tdd-email": fixture_tdd_email,
    "verify-pressure": fixture_verify_pressure,
}


def run_command(
    command: list[str],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def git(workdir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_command(["git", *args], workdir)


def initialize_fixture(workdir: Path, fixture: str) -> str:
    FIXTURES[fixture](workdir)
    skills_root = workdir / ".agents" / "skills"
    for skill_dir in sorted(path for path in ROOT.iterdir() if (path / "SKILL.md").is_file()):
        shutil.copytree(skill_dir, skills_root / skill_dir.name)

    commands = [
        ("init", "-b", "main"),
        ("config", "user.name", "Rightweight Eval"),
        ("config", "user.email", "eval@rightweight.invalid"),
        ("add", "-A"),
        ("commit", "-m", "fixture"),
    ]
    for args in commands:
        result = git(workdir, *args)
        if result.returncode != 0:
            raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return git(workdir, "rev-parse", "HEAD").stdout.strip()


def isolated_environment(home: Path) -> tuple[dict[str, str], str | None]:
    codex_home = home / ".codex"
    codex_home.mkdir(parents=True)
    source_codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    auth_source = source_codex_home / "auth.json"
    auth_note: str | None = None
    if auth_source.is_file():
        shutil.copy2(auth_source, codex_home / "auth.json")
    elif not os.environ.get("OPENAI_API_KEY"):
        auth_note = f"no Codex auth found at {auth_source} and OPENAI_API_KEY is unset"

    allow = {
        "COMSPEC",
        "LANG",
        "LC_ALL",
        "OPENAI_API_KEY",
        "PATH",
        "PATHEXT",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "WINDIR",
    }
    env = {key: value for key, value in os.environ.items() if key.upper() in allow}
    env.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "CODEX_HOME": str(codex_home),
            "APPDATA": str(home / "AppData" / "Roaming"),
            "LOCALAPPDATA": str(home / "AppData" / "Local"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local" / "share"),
            "XDG_STATE_HOME": str(home / ".local" / "state"),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "PYTHONUTF8": "1",
        }
    )
    return env, auth_note


def parse_events(stdout: str) -> tuple[list[dict[str, Any]], list[str]]:
    events: list[dict[str, Any]] = []
    rejected: list[str] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            rejected.append(stripped)
            continue
        if isinstance(value, dict):
            events.append(value)
    return events, rejected


def string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        result: list[str] = []
        for child in value.values():
            result.extend(string_values(child))
        return result
    if isinstance(value, list):
        result = []
        for child in value:
            result.extend(string_values(child))
        return result
    return []


def normalize_actions(events: list[dict[str, Any]]) -> list[Action]:
    actions: list[Action] = []
    for index, event in enumerate(events):
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        kind = str(item.get("type", "unknown"))
        item_id = str(item.get("id", index))

        paths: list[str] = []
        changes = item.get("changes")
        if isinstance(changes, list):
            for change in changes:
                if isinstance(change, dict) and isinstance(change.get("path"), str):
                    paths.append(change["path"].replace("\\", "/"))
        text = "\n".join(string_values(item))
        exit_code = item.get("exit_code")
        actions.append(
            Action(
                index=index,
                kind=kind,
                text=f"{item_id}\0{text}",
                paths=tuple(paths),
                exit_code=exit_code if isinstance(exit_code, int) else None,
            )
        )
    return actions


def command_actions(actions: list[Action], pattern: str) -> list[Action]:
    regex = re.compile(pattern, re.IGNORECASE)
    return [
        action
        for action in actions
        if action.kind in {"command_execution", "function_call", "tool_call"}
        and regex.search(action.text)
    ]


def file_change_actions(actions: list[Action], expected_path: str) -> list[Action]:
    normalized = expected_path.replace("\\", "/").lower()
    return [
        action
        for action in actions
        if action.kind == "file_change"
        and any(path.lower().endswith(normalized) for path in action.paths)
    ]


def skill_loaded(actions: list[Action], skill: str) -> bool:
    path_pattern = re.compile(
        rf"(?:[\\/]|\b){re.escape(skill)}[\\/]SKILL\.md\b|\${re.escape(skill)}\b",
        re.IGNORECASE,
    )
    observable_kinds = {"command_execution", "function_call", "mcp_tool_call", "skill", "tool_call"}
    return any(action.kind in observable_kinds and path_pattern.search(action.text) for action in actions)


def evaluate_check(
    check: dict[str, Any], workdir: Path, initial_head: str, actions: list[Action]
) -> tuple[bool, str]:
    check_type = check["type"]
    if check_type == "git-clean":
        result = git(workdir, "status", "--porcelain")
        clean = result.returncode == 0 and not result.stdout.strip()
        return clean, result.stdout.strip() or "worktree clean"
    if check_type == "head-unchanged":
        current = git(workdir, "rev-parse", "HEAD")
        passed = current.returncode == 0 and current.stdout.strip() == initial_head
        return passed, f"initial={initial_head} current={current.stdout.strip()}"
    if check_type == "skill-loaded":
        skill = check["skill"]
        passed = skill_loaded(actions, skill)
        return passed, f"observable skill load for {skill}: {passed}"
    if check_type == "trace-command":
        matches = command_actions(actions, check["command_pattern"])
        return bool(matches), f"matching command count={len(matches)}"
    if check_type == "command-succeeds":
        result = run_command(check["command"], workdir, timeout=120)
        detail = (result.stdout + result.stderr).strip()[-2000:]
        return result.returncode == 0, detail
    if check_type == "file-contains":
        path = workdir / check["path"]
        content = path.read_text(encoding="utf-8") if path.is_file() else ""
        passed = re.search(check["pattern"], content, re.MULTILINE) is not None
        return passed, f"{check['path']} matches pattern: {passed}"
    if check_type == "tdd-red-order":
        test_changes = file_change_actions(actions, check["test_path"])
        implementation_changes = file_change_actions(actions, check["implementation_path"])
        commands = command_actions(actions, check["command_pattern"])
        failing_commands = [command for command in commands if command.exit_code not in (None, 0)]
        passed = bool(test_changes and implementation_changes and failing_commands) and (
            test_changes[0].index < failing_commands[0].index < implementation_changes[0].index
        )
        detail = (
            f"test_change={test_changes[0].index if test_changes else None}, "
            f"failing_test={failing_commands[0].index if failing_commands else None}, "
            f"implementation_change={implementation_changes[0].index if implementation_changes else None}"
        )
        return passed, detail
    return False, f"unsupported check type: {check_type}"


def load_scenarios() -> list[dict[str, Any]]:
    document = json.loads(SCENARIOS_PATH.read_text(encoding="utf-8"))
    return document["scenarios"]


def skill_content_digest() -> str:
    digest = hashlib.sha256()
    paths = sorted(
        file
        for skill_dir in ROOT.iterdir()
        if (skill_dir / "SKILL.md").is_file()
        for file in skill_dir.rglob("*")
        if file.is_file()
    )
    for path in paths:
        digest.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def source_provenance() -> tuple[str | None, bool | None, str]:
    revision = git(ROOT, "rev-parse", "HEAD")
    status = git(ROOT, "status", "--porcelain")
    return (
        revision.stdout.strip() if revision.returncode == 0 else None,
        bool(status.stdout.strip()) if status.returncode == 0 else None,
        skill_content_digest(),
    )


def run_scenario(
    scenario: dict[str, Any],
    args: argparse.Namespace,
    artifact_root: Path,
    repetition: int,
) -> str:
    scenario_artifacts = artifact_root / scenario["id"] / f"rep-{repetition:02d}"
    scenario_artifacts.mkdir(parents=True, exist_ok=True)
    run_root = Path(tempfile.mkdtemp(prefix=f"rightweight-{scenario['id']}-"))
    workdir = run_root / "workspace"
    home = run_root / "home"
    workdir.mkdir()
    home.mkdir()
    revision, dirty, content_digest = source_provenance()
    result_document: dict[str, Any] = {
        "schema_version": 1,
        "scenario": scenario["id"],
        "repetition": repetition,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "model": args.model or "configured-default",
        "skills_revision": revision,
        "skills_dirty": dirty,
        "skills_content_sha256": content_digest,
        "status": "indeterminate",
        "checks": [],
    }

    try:
        initial_head = initialize_fixture(workdir, scenario["fixture"])
        env, auth_note = isolated_environment(home)
        if auth_note:
            result_document["reason"] = auth_note
            return write_result(scenario_artifacts, result_document)

        codex = shutil.which(args.codex, path=env.get("PATH"))
        if not codex:
            result_document["reason"] = f"Codex executable not found: {args.codex}"
            return write_result(scenario_artifacts, result_document)
        version = run_command([codex, "--version"], workdir, env=env)
        result_document["codex_version"] = (
            version.stdout.strip() if version.returncode == 0 else "unknown"
        )

        command = [
            codex,
            "exec",
            "--ephemeral",
            "--ignore-user-config",
            "--sandbox",
            "workspace-write",
            "--json",
            "-C",
            str(workdir),
        ]
        if args.model:
            command.extend(["--model", args.model])
        command.append(scenario["prompt"])

        try:
            completed = run_command(
                command,
                workdir,
                env=env,
                timeout=args.timeout or scenario.get("timeout_seconds", 600),
            )
        except subprocess.TimeoutExpired as exc:
            result_document["reason"] = f"Codex timed out after {exc.timeout} seconds"
            return write_result(scenario_artifacts, result_document)

        (scenario_artifacts / "trace.jsonl").write_text(completed.stdout, encoding="utf-8")
        (scenario_artifacts / "stderr.log").write_text(completed.stderr, encoding="utf-8")
        events, rejected = parse_events(completed.stdout)
        actions = normalize_actions(events)
        turn_completed = any(event.get("type") == "turn.completed" for event in events)
        if completed.returncode != 0 or not turn_completed:
            result_document["reason"] = (
                f"Codex run incomplete: exit={completed.returncode}, "
                f"turn_completed={turn_completed}, rejected_lines={len(rejected)}"
            )
            return write_result(scenario_artifacts, result_document)

        all_passed = True
        for check in scenario["checks"]:
            try:
                passed, detail = evaluate_check(check, workdir, initial_head, actions)
            except Exception as exc:  # A broken assertion is infrastructure, not behavior failure.
                result_document["reason"] = f"check {check['type']} crashed: {exc}"
                return write_result(scenario_artifacts, result_document)
            result_document["checks"].append(
                {"type": check["type"], "passed": passed, "detail": detail}
            )
            all_passed = all_passed and passed

        result_document["status"] = "pass" if all_passed else "fail"
        result_document["reason"] = "all checks passed" if all_passed else "one or more checks failed"
        return write_result(scenario_artifacts, result_document)
    except Exception as exc:
        result_document["reason"] = f"scenario setup or runner failed: {exc}"
        return write_result(scenario_artifacts, result_document)
    finally:
        if args.keep_workdir:
            shutil.copytree(workdir, scenario_artifacts / "workspace", dirs_exist_ok=True)
        shutil.rmtree(run_root, ignore_errors=True)


def write_result(artifact_dir: Path, document: dict[str, Any]) -> str:
    (artifact_dir / "verdict.json").write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"{document['scenario']}[rep-{document['repetition']:02d}]: "
        f"{document['status']} - {document.get('reason', '')}"
    )
    return document["status"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--scenario", action="append", help="scenario id; repeatable")
    selection.add_argument("--all", action="store_true", help="run all scenarios")
    selection.add_argument("--list", action="store_true", help="list scenarios without running")
    parser.add_argument("--codex", default="codex", help="Codex CLI executable")
    parser.add_argument("--model", help="optional model override")
    parser.add_argument("--repeat", type=int, default=1, help="repetitions per scenario")
    parser.add_argument("--timeout", type=int, help="per-scenario timeout in seconds")
    parser.add_argument(
        "--keep-workdir",
        action="store_true",
        help="copy fixture workspaces to artifacts; temporary auth is always deleted",
    )
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")

    scenarios = load_scenarios()
    if args.list:
        for scenario in scenarios:
            print(f"{scenario['id']}: {scenario['title']}")
        return 0

    selected_ids = set(args.scenario or [])
    if not args.all and not selected_ids:
        parser.error("select --all, --scenario ID, or --list")
    selected = [
        scenario for scenario in scenarios if args.all or scenario["id"] in selected_ids
    ]
    missing = selected_ids - {scenario["id"] for scenario in selected}
    if missing:
        parser.error(f"unknown scenario(s): {', '.join(sorted(missing))}")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_root = ROOT / ".artifacts" / "behavior" / stamp
    statuses = [
        run_scenario(scenario, args, artifact_root, repetition)
        for scenario in selected
        for repetition in range(1, args.repeat + 1)
    ]
    print(f"Artifacts: {artifact_root}")
    if "fail" in statuses:
        return 1
    if "indeterminate" in statuses:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
