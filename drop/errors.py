class DumbError(Exception):
    """testing error"""


class NoWarnError(Exception):
    """should occur when no warns are on a user"""


class NoRulesError(Exception):
    """No rules had been set for the guild according to its ID."""


class BrokenRulesError(Exception):
    """Rule file was invalid and had to be reset"""


class InvalidTimeParsed(Exception):
    """Wrong time format inputted, and it could not be parsed."""


class PastTimeError(Exception):
    """The time has been set to the past."""


class PresentTimeError(Exception):
    """The time has been set to now."""


class NoMutesForGuild(Exception):
    """There are no mutes for this guild."""


class NoMutesForUser(Exception):
    """The user does not have any mutes."""
