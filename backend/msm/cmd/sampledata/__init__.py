from msm.cmd._script import Script
from msm.cmd.sampledata._fixtures import DeleteFixturesAction, FixturesAction


class SampledataScript(Script):
    name = "maas-site-manager-sampledata"
    description = "Generate and purge sample data for MAAS Site Manager"

    actions = frozenset([FixturesAction, DeleteFixturesAction])


# script entry point
script = SampledataScript()
