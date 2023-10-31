from argparse import (
    ArgumentParser,
    Namespace,
)
from typing import Iterator

import pytest

from msm.cmd import (
    Action,
    Script,
)


@pytest.fixture
def action_class() -> Iterator[type[Action]]:
    class MyAction(Action):
        name = "my-action"
        description = "my action"

    yield MyAction


@pytest.fixture
def script_class(action_class: type[Action]) -> Iterator[type[Script]]:
    class MyScript(Script):
        description = "some script"

        actions = frozenset([action_class])

    yield MyScript


class TestScript:
    def test_setup_parser(self, script_class: type[Script]) -> None:
        script = script_class()
        assert script._parser.description == "some script"
        assert script._subparsers.metavar == "ACTION"

    def test_setup_actions(
        self, script_class: type[Script], action_class: type[Action]
    ) -> None:
        script = script_class()
        assert list(script._actions) == ["my-action"]
        assert isinstance(script._actions["my-action"], action_class)
        # the action is added as a command choice
        assert [choice for choice in script._subparsers.choices] == [
            "my-action"
        ]

    def test_call_action(
        self, script_class: type[Script], action_class: type[Action]
    ) -> None:
        calls = []

        class MyAction(action_class):  # type: ignore
            def register_options(self, parser: ArgumentParser) -> None:
                parser.add_argument("--opt")

            def execute(self, options: Namespace) -> int:
                calls.append(options)
                return 0

        script_class.actions = frozenset([MyAction])
        script = script_class()
        script(["my-action", "--opt", "foo"])
        assert calls == [Namespace(debug=False, action="my-action", opt="foo")]

    def test_call_exception_message(
        self,
        capsys: pytest.CaptureFixture[str],
        script_class: type[Script],
        action_class: type[Action],
    ) -> None:
        class MyAction(action_class):  # type: ignore
            def execute(self, options: Namespace) -> None:
                raise Exception("something went wrong")

        script_class.actions = frozenset([MyAction])
        script = script_class()
        with pytest.raises(SystemExit) as error:
            script(["my-action"])
        assert error.value.code == 2
        stderr = capsys.readouterr().err
        assert 'raise Exception("something went wrong")' not in stderr
        assert "Command failed: something went wrong" in stderr

    def test_call_exception_message_with_debug(
        self,
        capsys: pytest.CaptureFixture[str],
        script_class: type[Script],
        action_class: type[Action],
    ) -> None:
        class MyAction(action_class):  # type: ignore
            def execute(self, options: Namespace) -> None:
                raise Exception("something went wrong")

        script_class.actions = frozenset([MyAction])
        script = script_class()
        with pytest.raises(SystemExit) as error:
            script(["--debug", "my-action"])
        assert error.value.code == 2
        stderr = capsys.readouterr().err
        assert 'raise Exception("something went wrong")' in stderr
        assert "Command failed: something went wrong" in stderr

    def test_call_keyboard_interrupt(
        self,
        capsys: pytest.CaptureFixture[str],
        script_class: type[Script],
        action_class: type[Action],
    ) -> None:
        class MyAction(action_class):  # type: ignore
            def execute(self, options: Namespace) -> None:
                raise KeyboardInterrupt()

        script_class.actions = frozenset([MyAction])
        script = script_class()
        with pytest.raises(SystemExit) as error:
            script(["--debug", "my-action"])
        assert error.value.code == 0
        # no error is printed
        assert capsys.readouterr().err == ""
