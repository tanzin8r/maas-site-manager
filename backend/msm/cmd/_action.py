import argparse
import asyncio
from itertools import chain


class Action:
    """An action for a script."""

    name: str
    description: str

    def __init__(self) -> None:
        self._actions: dict[str, argparse.Action] = {}

    def __call__(self, options: argparse.Namespace) -> int:
        """Call the action."""
        return self.execute(options)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """Add options for the actions to the subparser."""
        self.register_options(parser)
        actions = chain(
            parser._positionals._group_actions,
            parser._optionals._group_actions,
        )
        self._actions = {action.dest: action for action in actions}

    def register_options(self, parser: argparse.ArgumentParser) -> None:
        """Register the Action with a subparser.

        Subclasses can implement this to add action-specific options to the
        parser.
        """

    def execute(self, options: argparse.Namespace) -> int:
        """Perform an action.

        Subclasses must implement this.
        """
        return 0


class AsyncAction(Action):
    """An asynchronous action for a Script."""

    def __call__(self, options: argparse.Namespace) -> int:
        """Call the action."""
        return asyncio.run(self.aexecute(options))

    async def aexecute(self, options: argparse.Namespace) -> int:
        """Perform an asyncronous action.

        Subclasses must implement this.
        """
        return 0
