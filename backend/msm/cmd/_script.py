import argparse
from operator import attrgetter
import sys
from traceback import format_tb

from msm.cmd._action import Action


class Script:
    """A CLI script."""

    name: str = ""
    description: str = ""
    actions: frozenset[type[Action]] = frozenset()

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            prog=self.name,
            description=self.description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self._parser.add_argument(
            "--debug",
            action="store_true",
            default=False,
            help="enable debug messages",
        )
        self._subparsers = self._parser.add_subparsers(
            metavar="ACTION", dest="action", help="action to perform"
        )
        self._subparsers.required = True
        self._actions = {
            action_class.name: self._register_action(action_class)
            for action_class in sorted(self.actions, key=attrgetter("name"))
        }

    def __call__(self, args: list[str] | None = None) -> int:
        """Execute the script."""
        options = self._parser.parse_args(args=args)
        # the action is guaranteed to be there as the parser validates choices
        action = self._actions[options.action]
        try:
            return action(options)
        except KeyboardInterrupt:
            do_exit()
        except Exception as e:
            message = ""
            if options.debug:
                _, _, traceback = sys.exc_info()
                message += "".join(format_tb(traceback))
            message += f"Command failed: {e!s}"
            do_exit(message, code=2)
        return 0

    def _register_action(self, action_class: type[Action]) -> Action:
        """Retister an Action."""
        action = action_class()
        parser = self._subparsers.add_parser(
            action.name,
            help=action.description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        action.add_arguments(parser)
        return action


def do_exit(message: str = "", code: int = 0) -> None:
    """Exit with the specified code, optionally printing a message."""
    if message:
        print(message, file=sys.stderr)
    raise SystemExit(code)
