from argparse import (
    Action as ArgparseAction,
    ArgumentParser,
)
from typing import Iterator

import pytest

from msm.cmd import Action


@pytest.fixture
def action_class() -> Iterator[type[Action]]:
    class MyAction(Action):
        name = "my-action"
        description = "my action"

    yield MyAction


class TestAction:
    def test_add_arguments(self, action_class: type[Action]) -> None:
        class MyAction(action_class):  # type: ignore
            def register_options(self, parser: ArgumentParser) -> None:
                parser.add_argument("--foo")
                parser.add_argument("--bar")

        parser = ArgumentParser()
        action = MyAction()
        action.add_arguments(parser)
        assert sorted(action._actions) == ["bar", "foo", "help"]
        for entry in action._actions.values():
            assert isinstance(entry, ArgparseAction)
