from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


RUNNER_PATH = Path(__file__).parent / "behavior" / "run.py"
SPEC = importlib.util.spec_from_file_location("rightweight_behavior_runner", RUNNER_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class BehaviorRunnerTests(unittest.TestCase):
    def test_skill_loading_requires_an_observable_tool_action(self) -> None:
        actions = [
            runner.Action(
                index=0,
                kind="agent_message",
                text="The user requested $test-driven.",
            ),
            runner.Action(
                index=1,
                kind="command_execution",
                text="type .agents/skills/test-driven/SKILL.md",
            ),
        ]

        self.assertTrue(runner.skill_loaded(actions, "test-driven"))
        self.assertFalse(runner.skill_loaded(actions[:1], "test-driven"))

    def test_tdd_red_order_requires_test_change_failure_then_implementation(self) -> None:
        actions = [
            runner.Action(
                index=2,
                kind="file_change",
                text="test change",
                paths=("tests/test_email_validator.py",),
            ),
            runner.Action(
                index=4,
                kind="command_execution",
                text="python -m unittest",
                exit_code=1,
            ),
            runner.Action(
                index=6,
                kind="file_change",
                text="implementation change",
                paths=("src/email_validator.py",),
            ),
        ]
        check = {
            "type": "tdd-red-order",
            "test_path": "tests/test_email_validator.py",
            "implementation_path": "src/email_validator.py",
            "command_pattern": "unittest",
        }

        passed, _ = runner.evaluate_check(check, Path.cwd(), "unused", actions)

        self.assertTrue(passed)

    def test_tdd_red_order_rejects_implementation_before_failure(self) -> None:
        actions = [
            runner.Action(
                index=2,
                kind="file_change",
                text="test change",
                paths=("tests/test_email_validator.py",),
            ),
            runner.Action(
                index=3,
                kind="file_change",
                text="implementation change",
                paths=("src/email_validator.py",),
            ),
            runner.Action(
                index=4,
                kind="command_execution",
                text="python -m unittest",
                exit_code=1,
            ),
        ]
        check = {
            "type": "tdd-red-order",
            "test_path": "tests/test_email_validator.py",
            "implementation_path": "src/email_validator.py",
            "command_pattern": "unittest",
        }

        passed, _ = runner.evaluate_check(check, Path.cwd(), "unused", actions)

        self.assertFalse(passed)

    def test_normalization_preserves_started_and_completed_event_order(self) -> None:
        events = [
            {
                "type": "item.started",
                "item": {"id": "cmd", "type": "command_execution", "command": "pytest"},
            },
            {
                "type": "item.completed",
                "item": {
                    "id": "cmd",
                    "type": "command_execution",
                    "command": "pytest",
                    "exit_code": 1,
                },
            },
        ]

        actions = runner.normalize_actions(events)

        self.assertEqual([action.index for action in actions], [0, 1])
        self.assertEqual(actions[1].exit_code, 1)


if __name__ == "__main__":
    unittest.main()
