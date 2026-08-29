#!/usr/bin/env python3
"""Validate Rightweight skill structure, metadata, docs, and eval scenarios."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", re.IGNORECASE)
SUPPORTED_FIXTURES = {"diagnose-only", "plan-only", "tdd-email", "verify-pressure"}
SUPPORTED_CHECKS = {
    "command-succeeds",
    "file-contains",
    "git-clean",
    "head-unchanged",
    "skill-loaded",
    "tdd-red-order",
    "trace-command",
}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def load_yaml(path: Path, validation: Validation) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        validation.error(f"{path}: cannot parse UTF-8 YAML: {exc}")
        return None


def discover_skills(root: Path) -> list[Path]:
    skills_root = root / "skills"
    if not skills_root.is_dir():
        skills_root = root
    return sorted(
        path for path in skills_root.iterdir() if path.is_dir() and (path / "SKILL.md").is_file()
    )


def validate_skill(skill_dir: Path, validation: Validation) -> str | None:
    skill_md = skill_dir / "SKILL.md"
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        validation.error(f"{skill_md}: cannot read as UTF-8: {exc}")
        return None

    match = FRONTMATTER_RE.match(content)
    if not match:
        validation.error(f"{skill_md}: missing YAML frontmatter")
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        validation.error(f"{skill_md}: invalid frontmatter: {exc}")
        return None

    if not isinstance(frontmatter, dict):
        validation.error(f"{skill_md}: frontmatter must be a mapping")
        return None

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) >= 64:
        validation.error(f"{skill_md}: name must be lowercase kebab-case under 64 characters")
        return None
    if name != skill_dir.name:
        validation.error(f"{skill_md}: name {name!r} does not match directory {skill_dir.name!r}")
    if not isinstance(description, str) or not description.strip():
        validation.error(f"{skill_md}: description must be a non-empty string")

    if PLACEHOLDER_RE.search(content):
        validation.error(f"{skill_md}: contains an unfinished placeholder")

    metadata_path = skill_dir / "agents" / "openai.yaml"
    if not metadata_path.is_file():
        validation.error(f"{metadata_path}: missing UI metadata")
        return name

    metadata = load_yaml(metadata_path, validation)
    if not isinstance(metadata, dict):
        return name
    interface = metadata.get("interface")
    if not isinstance(interface, dict):
        validation.error(f"{metadata_path}: interface must be a mapping")
        return name

    for key in ("display_name", "short_description", "default_prompt"):
        if not isinstance(interface.get(key), str) or not interface[key].strip():
            validation.error(f"{metadata_path}: interface.{key} must be a non-empty string")

    short_description = interface.get("short_description")
    if isinstance(short_description, str) and not 25 <= len(short_description) <= 64:
        validation.error(
            f"{metadata_path}: short_description must contain 25-64 characters "
            f"(found {len(short_description)})"
        )
    default_prompt = interface.get("default_prompt")
    if isinstance(default_prompt, str) and f"${name}" not in default_prompt:
        validation.error(f"{metadata_path}: default_prompt must mention ${name}")

    policy = metadata.get("policy", {})
    if not isinstance(policy, dict) or not isinstance(
        policy.get("allow_implicit_invocation", True), bool
    ):
        validation.error(f"{metadata_path}: policy.allow_implicit_invocation must be boolean")
    return name


def validate_readme(root: Path, skill_names: set[str], validation: Validation) -> None:
    readme = root / "README.md"
    try:
        content = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        validation.error(f"{readme}: cannot read as UTF-8: {exc}")
        return

    for name in sorted(skill_names):
        count = content.count(f"| `{name}` |")
        if count != 1:
            validation.error(f"{readme}: expected exactly one table row for {name}, found {count}")


def validate_markdown_links(root: Path, validation: Validation) -> None:
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts or ".artifacts" in path.parts:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            validation.error(f"{path}: cannot read as UTF-8: {exc}")
            continue
        for raw_target in LINK_RE.findall(content):
            target = raw_target.split("#", 1)[0].replace("%20", " ")
            if target and not (path.parent / target).resolve().exists():
                validation.error(f"{path}: broken relative link {raw_target!r}")


def validate_scenarios(root: Path, skill_names: set[str], validation: Validation) -> None:
    path = root / "tests" / "behavior" / "scenarios.json"
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        validation.error(f"{path}: cannot parse JSON: {exc}")
        return

    if not isinstance(document, dict) or document.get("schema_version") != 1:
        validation.error(f"{path}: schema_version must be 1")
        return
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        validation.error(f"{path}: scenarios must be a non-empty list")
        return

    seen: set[str] = set()
    for index, scenario in enumerate(scenarios):
        label = f"{path}: scenarios[{index}]"
        if not isinstance(scenario, dict):
            validation.error(f"{label} must be an object")
            continue
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not NAME_RE.fullmatch(scenario_id):
            validation.error(f"{label}.id must be lowercase kebab-case")
        elif scenario_id in seen:
            validation.error(f"{label}.id duplicates {scenario_id!r}")
        else:
            seen.add(scenario_id)
        if scenario.get("fixture") not in SUPPORTED_FIXTURES:
            validation.error(f"{label}.fixture is not supported")
        if not isinstance(scenario.get("prompt"), str) or not scenario["prompt"].strip():
            validation.error(f"{label}.prompt must be a non-empty string")
        skill = scenario.get("skill")
        if skill not in skill_names:
            validation.error(f"{label}.skill references unknown skill {skill!r}")
        checks = scenario.get("checks")
        if not isinstance(checks, list) or not checks:
            validation.error(f"{label}.checks must be a non-empty list")
            continue
        for check_index, check in enumerate(checks):
            if not isinstance(check, dict) or check.get("type") not in SUPPORTED_CHECKS:
                validation.error(f"{label}.checks[{check_index}] has an unsupported type")


def run_official_validator(root: Path, skills: list[Path], requested: str | None, validation: Validation) -> None:
    if requested:
        validator = Path(requested).expanduser().resolve()
    else:
        validator = (
            Path.home()
            / ".codex"
            / "skills"
            / ".system"
            / "skill-creator"
            / "scripts"
            / "quick_validate.py"
        )
    if not validator.is_file():
        validation.error(f"official validator not found: {validator}")
        return

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    for skill_dir in skills:
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(validator), str(skill_dir)],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip()
            validation.error(f"{skill_dir}: official validator failed: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--official",
        nargs="?",
        const="",
        metavar="QUICK_VALIDATE_PATH",
        help="also run skill-creator quick_validate.py; optionally provide its path",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    validation = Validation()
    skills = discover_skills(root)
    if not skills:
        validation.error(f"{root}: no skills found under skills/ or repository root")

    names = {name for skill in skills if (name := validate_skill(skill, validation))}
    if len(names) != len(skills):
        validation.error("skill names must be unique and valid")
    validate_readme(root, names, validation)
    validate_markdown_links(root, validation)
    validate_scenarios(root, names, validation)

    if args.official is not None:
        run_official_validator(root, skills, args.official or None, validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}")
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if validation.errors:
        print(f"Validation failed with {len(validation.errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validated {len(skills)} skills and behavior scenario schema successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
