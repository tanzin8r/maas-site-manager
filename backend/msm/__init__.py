from pkg_resources import get_distribution

__all__ = [
    "PACKAGE",
    "__version__",
]


PACKAGE = get_distribution("msm")

__version__ = PACKAGE.version
