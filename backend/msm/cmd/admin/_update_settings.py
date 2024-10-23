from argparse import (
    ArgumentParser,
    Namespace,
)

from msm.cmd import (
    DatabaseAction,
)
from msm.db.models._settings import SettingsUpdate
from msm.service import SettingsService


class UpdateSettingsAction(DatabaseAction):
    name = "update-settings"
    description = "Update settings"

    def register_options(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--service_url",
            help="The base URL for the API.",
            required=False,
            type=str,
            default=None,
        )

        parser.add_argument(
            "--token_lifetime_minutes",
            help="Lifetime of access tokens in minutes.",
            required=False,
            type=int,
            default=None,
        )

        parser.add_argument(
            "--token_rotation_interval_minutes",
            help="Interval for rotating access tokens in minutes.",
            required=False,
            type=int,
            default=None,
        )

    async def aexecute(self, options: Namespace) -> int:
        await self._update_setting(
            SettingsUpdate(**(dict(options._get_kwargs())))
        )
        return 0

    async def _update_setting(self, request: SettingsUpdate) -> None:
        async with self.database_connection() as conn:
            settings = SettingsService(conn)
            await settings.update(request.model_dump(exclude_none=True))
