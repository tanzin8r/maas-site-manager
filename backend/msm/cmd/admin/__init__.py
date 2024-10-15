from msm.cmd._script import Script
from msm.cmd.admin._create_user import CreateUserAction
from msm.cmd.admin._update_settings import UpdateSettingsAction


class AdminScript(Script):
    name = "maas-site-manager"
    description = "MAAS Site Manager - management tool"

    actions = frozenset([CreateUserAction, UpdateSettingsAction])


# script entry point
script = AdminScript()
