"""
This module contains data classes for interaction with LanguageTool.
"""

from __future__ import annotations
from dataclasses import dataclass
import re

LT_REPLACEMENT_SEPARATOR = "@|@"

LT_MATCH_REGEX = re.compile(
    r"^\((?P<rule>[^,]+),(?P<start>[0-9]+),(?P<end>[0-9]+)\)"
    + r"\{(?P<replacements>[^}]*)\}$"
)


@dataclass
class LTRule:
    """
    This class holds information about a LanguageTool rule.
    """

    rule_id: str
    description: str
    issue_type: str
    category: tuple[str, str]


@dataclass
class LTContext:
    """
    This class holds information about the context of a LanguageTool match.
    """

    text: str
    offset: int
    length: int


@dataclass
class LTMatch:
    """
    This class holds a single match from language tool,
    i.e., the output from one single rule firing for a specific text span.

    Attributes:
        rule: LT rule ID
        start: character offset of the start of the match
        end: character offset of the end of the match
        replacements: sequence of suggestions from LT to fix the mistake
    """

    rule: LTRule
    start: int
    end: int
    replacements: tuple[str, ...]
    message: str
    short_message: str
    context: LTContext


@dataclass
class LightweightMatch:
    """
    This class is a lightweight variant of `LTMatch`
    used to easily store the essential information as a (not too long) string.
    """

    rule: str
    start: int
    end: int
    replacements: tuple[str, ...]

    @staticmethod
    def from_short_string(
        serialization: str, replacement_separator: str = LT_REPLACEMENT_SEPARATOR
    ) -> LightweightMatch:
        match = LT_MATCH_REGEX.match(serialization)
        if match is None:
            raise ValueError(f"Malformed LT annotation string: {serialization}")

        serialized_replacements: str = match.group("replacements")
        replacements = tuple(serialized_replacements.split(replacement_separator))
        parsed_annotation = LightweightMatch(
            match.group("rule"),
            int(match.group("start")),
            int(match.group("end")),
            replacements,
        )
        return parsed_annotation

    def to_short_string(self) -> str:
        return (
            "("
            + self.rule
            + ","
            + str(self.start)
            + ","
            + str(self.end)
            + "){"
            + LT_REPLACEMENT_SEPARATOR.join(self.replacements)
            + "}"
        )
