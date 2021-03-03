class DumbError(Exception):
    """testing error"""


class NoWarnError(Exception):
    """should occur when no warns are on a user"""


class InvalidWarn(Exception):
    """Wrong warn index, probably."""
