from msm.cmd._script import Script
from msm.cmd.sampledata._fixtures import FixturesAction


class SampledataScript(Script):
    name = "maas-site-manager-sampledata"
    description = "Generate sample data for MAAS Site Manager"

    actions = frozenset([FixturesAction])


# script entry point
script = SampledataScript()
