"""
Grammar definitions for screenplay parsing based on The Hollywood Standard.

This module defines the pyparsing grammar for shot headings, transitions,
and other screenplay elements according to industry standards.
"""

from typing import List, Set
import pyparsing as pp
from enum import Enum


# Basic character sets and tokens
CAPS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LOWER = CAPS.lower()
DIGITS = "0123456789"
ALPHANUMS = CAPS + DIGITS + "'" + "\\" + "/" + '"' + "'" + "_" + "," + "-" + "."
ALL_CHARS = ALPHANUMS + LOWER

# Whitespace and punctuation
WH = pp.White().suppress()
HYPHEN = WH + pp.Literal("-").suppress() + WH
OHYPHEN = pp.Literal("-").suppress() + WH
LP = pp.Literal("(")
RP = pp.Literal(")")
EOL = pp.Or(pp.LineEnd().suppress(), pp.Literal("\n"))


class ShotTypeEnum(str, Enum):
    """Enumeration of shot types."""
    CLOSE = "CLOSE"
    EXTREME_CLOSE = "EXTREME CLOSE"
    WIDE = "WIDE"
    MEDIUM = "MEDIUM"
    TWO_SHOT = "TWO SHOT"
    THREE_SHOT = "THREE SHOT"
    ESTABLISHING = "ESTABLISHING"
    TRACKING = "TRACKING"
    MOVING = "MOVING"
    ANGLE = "ANGLE"
    REVERSE = "REVERSE"
    CRANE = "CRANE"
    TILT = "TILT"
    PAN = "PAN"
    ZOOM = "ZOOM"
    POV = "POV"
    INSERT = "INSERT"
    AERIAL = "AERIAL"
    UNDERWATER = "UNDERWATER"
    HANDHELD = "HANDHELD"


# Shot type definitions
CLOSE = pp.Combine(
    pp.Or([
        pp.Literal("CLOSE"),
        pp.Literal("CLOSE SHOT"),
        pp.Literal("CLOSEUP"),
        pp.Literal("CLOSE ANGLE"),
        pp.Literal("CLOSE-UP"),
    ]).setResultsName("close"),
    joinString=" ",
    adjacent=False,
)

XCLOSE = pp.Or([
    pp.Literal("EXTREME CLOSEUP"),
    pp.Literal("EXTREME CLOSE-UP"),
    pp.Literal("TIGHT CLOSE"),
    pp.Literal("ECU"),
]).setResultsName("extreme_close")

WIDE = pp.Or([
    pp.Literal("WIDE"),
    pp.Literal("WIDE SHOT"),
    pp.Literal("WIDE ANGLE"),
    pp.Literal("WS"),
]).setResultsName("wide")

MEDIUM = pp.Or([
    pp.Literal("MED. SHOT"),
    pp.Literal("MEDIUM SHOT"),
    pp.Literal("MED"),
    pp.Literal("MS"),
]).setResultsName("medium")

TWO_SHOT = pp.Or([
    pp.Literal("TWO SHOT"),
    pp.Literal("2 SHOT"),
    pp.Literal("TWO-SHOT"),
]).setResultsName("two_shot")

THREE_SHOT = pp.Or([
    pp.Literal("THREE SHOT"),
    pp.Literal("3 SHOT"),
    pp.Literal("THREE-SHOT"),
]).setResultsName("three_shot")

ESTABLISHING = pp.Or([
    pp.Literal("ESTABLISHING SHOT"),
    pp.Literal("ESTABLISHING"),
    pp.Literal("(ESTABLISHING)"),
    pp.Literal("TO ESTABLISH"),
    pp.Literal("EST"),
]).setResultsName("establishing")

# Camera movement shots
TRACKING = pp.Or([
    pp.Literal("TRACKING SHOT"),
    pp.Literal("TRACKING"),
    pp.Literal("DOLLY"),
    pp.Literal("DOLLY SHOT"),
]).setResultsName("tracking")

MOVING = pp.Or([
    pp.Literal("MOVING"),
    pp.Literal("MOVING SHOT"),
    pp.Literal("STEADICAM"),
]).setResultsName("moving")

ANGLE = pp.Or([
    pp.Literal("NEW ANGLE"),
    pp.Literal("ANGLE"),
    pp.Literal("UP ANGLE"),
    pp.Literal("DOWN ANGLE"),
    pp.Literal("HIGH ANGLE"),
    pp.Literal("LOW ANGLE"),
    pp.Literal("ANGLE ON"),
]).setResultsName("angle")

REVERSE = pp.Or([
    pp.Literal("REVERSE ANGLE"),
    pp.Literal("REVERSE"),
    pp.Literal("REVERSE SHOT"),
]).setResultsName("reverse")

CRANE = pp.Literal("CRANE").setResultsName("crane")
TILT = pp.Literal("TILT").setResultsName("tilt")
PAN = pp.Literal("PAN").setResultsName("pan")
ZOOM = pp.Literal("ZOOM").setResultsName("zoom")

# POV shots
WHAT_X_SEES = pp.Combine(
    pp.Literal("WHAT") + pp.Word(ALPHANUMS) + pp.Literal("SEES"),
    joinString=" ",
    adjacent=False,
)

X_POV = pp.Combine(
    pp.Word(ALPHANUMS) + pp.Literal("'S POV"),
    joinString="",
    adjacent=False,
)

POV = pp.Or([
    pp.Literal("P.O.V."),
    pp.Literal("POV"),
    pp.Literal("POINT OF VIEW"),
    pp.Literal("MYSTERY POV"),
    pp.Literal("ANONYMOUS POV"),
    pp.Literal("THROUGH SNIPER SCOPE"),
    pp.Literal("POV SHOT"),
    pp.Literal("BINOCULAR POV"),
    pp.Literal("MICROSCOPIC POV"),
    pp.Literal("SUBJECTIVE CAMERA"),
    WHAT_X_SEES,
    X_POV,
]).setResultsName("pov")

# Special shots
INSERT = pp.Or([
    pp.Literal("INSERT SHOT"),
    pp.Literal("INSERT"),
]).setResultsName("insert")

AERIAL = pp.Or([
    pp.Literal("AERIAL"),
    pp.Literal("AERIAL SHOT"),
    pp.Literal("HELICOPTER SHOT"),
]).setResultsName("aerial")

UNDERWATER = pp.Or([
    pp.Literal("UNDERWATER"),
    pp.Literal("UNDERWATER SHOT"),
]).setResultsName("underwater")

HANDHELD = pp.Or([
    pp.Literal("HANDHELD SHOT"),
    pp.Literal("HANDHELD"),
    pp.Literal("(HANDHELD)"),
]).setResultsName("handheld")

# Combine all shot types
SHOT_TYPES = pp.Or([
    CLOSE,
    XCLOSE,
    WIDE,
    MEDIUM,
    TWO_SHOT,
    THREE_SHOT,
    ESTABLISHING,
    TRACKING,
    MOVING,
    ANGLE,
    REVERSE,
    CRANE,
    TILT,
    PAN,
    ZOOM,
    POV,
    INSERT,
    AERIAL,
    UNDERWATER,
    HANDHELD,
]).setResultsName("shot_type")

# Prepositions
BASIC_PREP = pp.oneOf([
    "ON", "OF", "WITH", "TO", "TOWARDS", "FROM", "IN",
    "UNDER", "OVER", "ABOVE", "AROUND", "INTO", "THROUGH"
])
PREP = BASIC_PREP + WH

# Transitions
CUT = pp.Literal("CUT")
DISSOLVE = pp.Literal("DISSOLVE")
FADE = pp.Literal("FADE")
WIPE = pp.Literal("WIPE")
MATCH = pp.Literal("MATCH")
HARD = pp.Literal("HARD")

TRANSITION_TYPES = [
    "CUT TO:",
    "FADE IN:",
    "FADE OUT.",
    "FADE TO BLACK.",
    "DISSOLVE TO:",
    "MATCH CUT TO:",
    "HARD CUT TO:",
    "WIPE TO:",
    "SMASH CUT TO:",
    "TIME CUT TO:",
    "JUMP CUT TO:",
    "FADE TO:",
]

TRANSITIONS = pp.Combine(
    pp.Optional(pp.Word(ALPHANUMS)) +
    pp.Or([CUT, DISSOLVE, FADE, WIPE, MATCH, HARD]) +
    pp.Optional(pp.Word(ALPHANUMS)) +
    pp.Optional(pp.Literal(":").suppress()),
    joinString=" ",
    adjacent=False,
).setResultsName("transition")

# Intercut and montage
INTERCUT = pp.Or([
    pp.Literal("INTERCUTTING"),
    pp.Literal("INTERCUT"),
    pp.Literal("CUTTING"),
    pp.Literal("CUTS"),
    pp.Literal("MONTAGE"),
    pp.Literal("VARIOUS SHOTS"),
    pp.Literal("SERIES OF SHOTS"),
]).setResultsName("intercut")

# Time of day words
TIME_WORDS: Set[str] = {
    "sunrise", "sunset", "dawn", "dusk", "twilight",
    "morning", "afternoon", "evening", "night", "noon", "midnight",
    "day", "continuous", "later", "moments later",
    "present", "past", "future",
    "spring", "summer", "fall", "autumn", "winter",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "christmas", "easter", "thanksgiving", "halloween",
    "birthday", "anniversary", "wedding",
}

ENUMERATED_TIME_WORD = pp.oneOf(list(TIME_WORDS), caseless=False)

# Location types
INT = pp.Or([pp.Literal("INT."), pp.Literal("INT")]).setResultsName("interior")
EXT = pp.Or([pp.Literal("EXT."), pp.Literal("EXT")]).setResultsName("exterior")
INT_EXT = pp.Or([
    pp.Literal("INT./EXT."),
    pp.Literal("INT/EXT"),
    pp.Literal("I/E"),
]).setResultsName("int_ext")

LOCATION_TYPE = pp.Or([INT_EXT, INT, EXT]).setResultsName("location_type")

# Segment parsing helpers
IN_CAPS = pp.OneOrMore(pp.Word(ALPHANUMS), stopOn=pp.Or(HYPHEN, EOL))
IN_CAPS_W_CONDITION = IN_CAPS.addCondition(
    lambda toks: len(toks) > 1 or len(toks[0]) > 1
)
CAPS_SEGMENT = pp.Combine(IN_CAPS_W_CONDITION, joinString=" ", adjacent=False)

# Title detection (for character names)
TITLE = pp.Combine(
    pp.Word(ALPHANUMS, exact=1) + pp.Word(LOWER),
    joinString="",
    adjacent=True,
)

# Indentation parsing
def num_spaces(tokens):
    """Count the number of spaces in indentation."""
    return len(tokens[0])

SPACES = pp.OneOrMore(pp.White(ws=" ", min=1)).addParseAction(num_spaces)
MIN_2_SPACES = pp.OneOrMore(pp.White(ws=" ", min=2)).addParseAction(num_spaces)


# Helper functions
def is_time_expression(text: str) -> bool:
    """Check if text contains a time expression."""
    text_lower = text.lower()
    for time_word in TIME_WORDS:
        if time_word in text_lower:
            return True

    # Check for time patterns (e.g., "3 AM", "10:30")
    import re
    time_patterns = [
        r"\b\d{1,2}:\d{2}\b",  # 10:30
        r"\b\d{1,2}\s*[AP]\.?M\.?\b",  # 3 AM, 10 P.M.
        r"\b\d{4}\b",  # Year (1999)
    ]

    for pattern in time_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


def is_shot_type(text: str) -> bool:
    """Check if text contains a shot type."""
    shot_keywords = [
        "SHOT", "ANGLE", "CLOSE", "WIDE", "MEDIUM", "POV",
        "TRACKING", "PAN", "TILT", "ZOOM", "CRANE",
        "AERIAL", "INSERT", "ESTABLISHING",
    ]

    text_upper = text.upper()
    for keyword in shot_keywords:
        if keyword in text_upper:
            return True

    return False


# Export key components
__all__ = [
    # Character sets
    "CAPS", "LOWER", "DIGITS", "ALPHANUMS", "ALL_CHARS",

    # Basic tokens
    "WH", "HYPHEN", "OHYPHEN", "LP", "RP", "EOL",

    # Shot types
    "SHOT_TYPES", "ShotTypeEnum",

    # Transitions
    "TRANSITIONS", "TRANSITION_TYPES",

    # Location types
    "LOCATION_TYPE", "INT", "EXT", "INT_EXT",

    # Time expressions
    "TIME_WORDS", "ENUMERATED_TIME_WORD", "is_time_expression",

    # Helper functions
    "is_shot_type", "is_time_expression",

    # Parsing helpers
    "CAPS_SEGMENT", "TITLE", "SPACES", "MIN_2_SPACES",
]