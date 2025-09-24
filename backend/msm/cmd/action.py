import argparse
import asyncio
from collections.abc import AsyncIterator
from contextlib import (
    aclosing,
    asynccontextmanager,
)
from functools import cached_property
from itertools import chain

from sqlalchemy.ext.asyncio import AsyncConnection

from msm.apiserver.db import Database
from msm.common.settings import Settings


class Action:
    """An action for a script."""

    name: str
    description: str

    def __init__(self) -> None:
        self._actions: dict[str, argparse.Action] = {}

    def __call__(self, options: argparse.Namespace) -> int:
        """Call the action."""
        return self.execute(options)

    @cached_property
    def settings(self) -> Settings:
        """Application settings."""
        return Settings()

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


class DatabaseAction(AsyncAction):
    """An action with database access."""

    @cached_property
    def db(self) -> Database:
        return Database(self.settings.db_dsn())

    @asynccontextmanager
    async def database_connection(self) -> AsyncIterator[AsyncConnection]:
        """Context manager to execute code in a database transaction."""
        async with aclosing(self.db), self.db.transaction() as conn:
            yield conn
