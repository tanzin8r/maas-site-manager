from argparse import (
    ArgumentParser,
    Namespace,
)

from msm.cmd import (
    DatabaseAction,
    do_exit,
)
from msm.db.models import UserCreate
from msm.service import UserService


class CreateUserAction(DatabaseAction):
    name = "create-user"
    description = "Create a user"

    def register_options(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "username",
            help="Username for the new user",
        )
        parser.add_argument(
            "email",
            help="User e-mail",
        )
        parser.add_argument(
            "full_name",
            help="Full name",
        )
        parser.add_argument(
            "password",
            help="User password",
        )
        parser.add_argument(
            "--admin",
            help="Make the user an admin",
            action="store_true",
            default=False,
        )

    async def aexecute(self, options: Namespace) -> int:
        await self._create_user(
            options.username,
            options.email,
            options.full_name,
            options.password,
            options.admin,
        )
        return 0

    async def _create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        password: str,
        admin: bool,
    ) -> None:
        async with self.database_connection() as conn:
            users = UserService(conn)
            if await users.exists(email=email, username=username):
                do_exit(
                    "User with specified username/email already exists.",
                    code=1,
                )

            await users.create(
                UserCreate(
                    username=username,
                    email=email,
                    full_name=full_name,
                    password=password,
                    is_admin=admin,
                )
            )
