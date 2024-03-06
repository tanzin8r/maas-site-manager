from argparse import Namespace

from sqlalchemy.ext.asyncio import AsyncConnection

from msm.api import ensure_db_entries
from msm.cmd import DatabaseAction
from msm.db.models import Config
from msm.sampledata import (
    SampleDataModel,
    make_fixture_sites,
    make_fixture_tokens,
    make_fixture_users,
)
from msm.service import ConfigService


class FixturesAction(DatabaseAction):
    name = "create-fixtures"
    description = "Create fixed sample data fixtures"

    async def aexecute(self, options: Namespace) -> int:
        async with self.database_connection() as conn:
            await self.db.ensure_schema()
            await self.db.execute_in_transaction(ensure_db_entries)
            config = await self._get_config(conn)
            await self._make_fixtures(conn, config)

        return 0

    async def _get_config(self, conn: AsyncConnection) -> Config:
        service = ConfigService(conn)
        return await service.get()

    async def _make_fixtures(
        self, conn: AsyncConnection, config: Config
    ) -> None:
        users = await make_fixture_users(conn)
        self._print_fixtures("users", ["id", "username", "email"], users)
        sites = await make_fixture_sites(conn)
        self._print_fixtures("sites", ["id", "name", "url"], sites)
        tokens = await make_fixture_tokens(
            conn,
            config.service_identifier,
            config.token_secret_key,
        )
        self._print_fixtures("tokens", ["id", "value", "expired"], tokens)

    def _print_fixtures(
        self, entity: str, attribs: list[str], fixtures: list[SampleDataModel]
    ) -> None:
        print(f"Creating {len(fixtures)} {entity}:")
        for entry in fixtures:
            print(
                " "
                + " | ".join(str(getattr(entry, attrib)) for attrib in attribs)
            )
