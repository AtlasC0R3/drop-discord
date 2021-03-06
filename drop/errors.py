class DumbError(Exception):
    """testing error"""


class NoWarnError(Exception):
    """should occur when no warns are on a user"""


class NoRulesError(Exception):
    """No rules had been set for the guild according to its ID."""


class BrokenRulesError(Exception):
    """Rule file was invalid and had to be reset"""
