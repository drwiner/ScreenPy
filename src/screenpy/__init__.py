"""
ScreenPy: Automated Screenplay Annotation for Extracting Storytelling Knowledge

A Python package for parsing and analyzing screenplays to extract structured
narrative elements and storytelling patterns.
"""

__version__ = "2.0.0"
__author__ = "David R. Winer"
__email__ = "drwiner@cs.utah.edu"

from screenpy.parser import ScreenplayParser
from screenpy.models import Screenplay, Segment, ShotHeading

__all__ = [
    "ScreenplayParser",
    "Screenplay",
    "Segment",
    "ShotHeading",
]