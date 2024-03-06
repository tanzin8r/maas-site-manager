from msm.cmd._script import Script
from msm.cmd.admin._create_user import CreateUserAction


class AdminScript(Script):
    name = "maas-site-manager"
    description = "MAAS Site Manager - management tool"

    actions = frozenset([CreateUserAction])


# script entry point
script = AdminScript()
