"""
Core screenplay parser implementation using pyparsing.

Based on the grammar defined in the INT17 paper and The Hollywood Standard.
"""

from typing import List, Dict, Optional, Tuple, Any
import logging
import re
from pathlib import Path
import pyparsing as pp
from datetime import datetime

from screenpy.models import (
    Screenplay,
    Segment,
    ShotHeading,
    Dialogue,
    Transition,
    Character,
    LocationType,
    SegmentType,
    TransitionType,
)
from screenpy.parser.grammar import (
    LOCATION_TYPE,
    SHOT_TYPES,
    TRANSITIONS,
    TIME_WORDS,
    CAPS_SEGMENT,
    TITLE,
    HYPHEN,
    WH,
    is_time_expression,
    is_shot_type,
)
from screenpy.parser.time_parser import TimeParser
from screenpy.parser.shot_parser import ShotHeadingParser

logger = logging.getLogger(__name__)


class ScreenplayParser:
    """
    Main parser for screenplay text files.

    Parses raw screenplay text into structured Screenplay objects
    with hierarchical segment relationships.
    """

    def __init__(self, strict: bool = False):
        """
        Initialize the parser.

        Args:
            strict: If True, raise exceptions on parse errors.
                   If False, log warnings and continue.
        """
        self.strict = strict
        self.time_parser = TimeParser()
        self.shot_parser = ShotHeadingParser()
        self._init_patterns()

    def _init_patterns(self):
        """Initialize regex patterns for element detection."""
        # Indentation patterns
        self.center_indent = re.compile(r"^\s{20,}")
        self.right_indent = re.compile(r"^\s{40,}")
        self.dialogue_indent = re.compile(r"^\s{10,30}")

        # Element patterns
        self.page_number = re.compile(r"^\s*\d+\.?\s*$")
        self.continued = re.compile(r"\(CONTINUED\)|\(CONT'D\)")
        self.more = re.compile(r"\(MORE\)")
        self.parenthetical = re.compile(r"^\s*\([^)]+\)\s*$")

        # Character modifiers
        self.char_modifiers = re.compile(
            r"\((V\.O\.|O\.S\.|O\.C\.|CONT'D|CONT|CONT\.|OFF)\)"
        )

        # In-line caps (emphasized elements in stage direction)
        self.inline_caps = re.compile(r"\b[A-Z][A-Z]+\b")

    def parse(self, text: str) -> Screenplay:
        """
        Parse screenplay text into structured format.

        Args:
            text: Raw screenplay text

        Returns:
            Parsed Screenplay object
        """
        lines = text.split("\n")
        segments = []
        current_segment_id = 0
        parent_stack = []
        characters = {}
        transitions = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Skip empty lines and page numbers
            if not line.strip() or self.page_number.match(line):
                i += 1
                continue

            # Try to parse as shot heading
            heading = self._parse_shot_heading(line, i)
            if heading:
                segment = Segment(
                    id=current_segment_id,
                    type=SegmentType.SHOT_HEADING,
                    heading=heading,
                    content="",
                    start_pos=i,
                    end_pos=i,
                )

                # Handle hierarchy
                if heading.is_master:
                    # Close any open non-master segments
                    parent_stack = [current_segment_id]
                else:
                    # This is a sub-segment
                    if parent_stack:
                        segment.parent_segment_id = parent_stack[-1]
                        # Add to parent's children
                        if segments:
                            parent = segments[parent_stack[-1]]
                            parent.child_segment_ids.append(current_segment_id)

                segments.append(segment)
                current_segment_id += 1
                i += 1

                # Check for stage direction following heading
                i = self._parse_stage_direction(lines, i, segment)
                continue

            # Try to parse as transition
            transition = self._parse_transition(line)
            if transition:
                transitions.append(transition)
                i += 1
                continue

            # Try to parse as dialogue
            dialogue_result = self._parse_dialogue_block(lines, i)
            if dialogue_result:
                dialogue, end_i = dialogue_result

                # Track character
                char_name = dialogue.character.name
                characters[char_name] = characters.get(char_name, 0) + 1

                segment = Segment(
                    id=current_segment_id,
                    type=SegmentType.DIALOGUE,
                    dialogue=dialogue,
                    content=dialogue.text,
                    start_pos=i,
                    end_pos=end_i,
                )

                if parent_stack:
                    segment.parent_segment_id = parent_stack[-1]

                segments.append(segment)
                current_segment_id += 1
                i = end_i + 1
                continue

            # Default to stage direction
            segment = Segment(
                id=current_segment_id,
                type=SegmentType.STAGE_DIRECTION,
                content=line.strip(),
                capitalized_words=self._extract_caps(line),
                start_pos=i,
                end_pos=i,
            )

            if parent_stack:
                segment.parent_segment_id = parent_stack[-1]

            segments.append(segment)
            current_segment_id += 1
            i += 1

        # Create screenplay object
        title = self._extract_title(text)

        return Screenplay(
            title=title,
            segments=segments,
            transitions=transitions,
            characters=characters,
            metadata={
                "parse_date": datetime.now().isoformat(),
                "parser_version": "2.0.0",
            },
        )

    def _parse_shot_heading(
        self, line: str, line_num: int
    ) -> Optional[ShotHeading]:
        """
        Parse a line as a shot heading.

        Returns None if not a shot heading.
        """
        line = line.strip()

        # Must be in all caps (with some exceptions)
        if not line.isupper():
            # Check for mixed case headings (less common)
            if not any(keyword in line.upper() for keyword in ["INT.", "EXT.", "SHOT", "ANGLE"]):
                return None

        return self.shot_parser.parse(line, line_num)

    def _parse_transition(self, line: str) -> Optional[Transition]:
        """Parse a line as a transition."""
        line = line.strip()

        # Transitions are right-aligned or end with ":"
        if not (self.right_indent.match(line) or line.endswith(":")):
            return None

        # Check for transition keywords
        trans_keywords = [
            "CUT", "FADE", "DISSOLVE", "WIPE",
            "MATCH", "JUMP", "SMASH", "TIME"
        ]

        line_upper = line.upper()
        for keyword in trans_keywords:
            if keyword in line_upper:
                # Determine transition type
                trans_type = TransitionType.OTHER
                if "CUT TO" in line_upper:
                    if "MATCH" in line_upper:
                        trans_type = TransitionType.MATCH_CUT
                    elif "HARD" in line_upper:
                        trans_type = TransitionType.HARD_CUT
                    else:
                        trans_type = TransitionType.CUT_TO
                elif "FADE IN" in line_upper:
                    trans_type = TransitionType.FADE_IN
                elif "FADE OUT" in line_upper:
                    trans_type = TransitionType.FADE_OUT
                elif "DISSOLVE" in line_upper:
                    trans_type = TransitionType.DISSOLVE_TO
                elif "WIPE" in line_upper:
                    trans_type = TransitionType.WIPE_TO

                return Transition(type=trans_type, text=line)

        return None

    def _parse_dialogue_block(
        self, lines: List[str], start_i: int
    ) -> Optional[Tuple[Dialogue, int]]:
        """
        Parse a dialogue block starting at the given line.

        Returns (Dialogue, end_line_index) or None.
        """
        if start_i >= len(lines):
            return None

        line = lines[start_i]

        # Character names are center-indented and in caps
        if not self.center_indent.match(line):
            return None

        char_line = line.strip()
        if not char_line or not char_line[0].isupper():
            return None

        # Extract character name and modifier
        char_match = self.char_modifiers.search(char_line)
        if char_match:
            char_name = char_line[: char_match.start()].strip()
            modifier = char_match.group(1)
        else:
            char_name = char_line
            modifier = None

        character = Character(name=char_name, modifier=modifier)

        # Look for dialogue text
        i = start_i + 1
        dialogue_lines = []
        parenthetical = None

        while i < len(lines):
            line = lines[i]

            # Empty line might end dialogue
            if not line.strip():
                # Check if next line continues dialogue
                if i + 1 < len(lines) and self.dialogue_indent.match(lines[i + 1]):
                    i += 1
                    continue
                else:
                    break

            # Check for parenthetical
            if self.parenthetical.match(line):
                parenthetical = line.strip()
                i += 1
                continue

            # Check if line is dialogue (indented but not center)
            if self.dialogue_indent.match(line) and not self.center_indent.match(line):
                dialogue_lines.append(line.strip())
                i += 1
            else:
                break

        if not dialogue_lines:
            return None

        dialogue = Dialogue(
            character=character,
            parenthetical=parenthetical,
            text=" ".join(dialogue_lines),
        )

        return dialogue, i - 1

    def _parse_stage_direction(
        self, lines: List[str], start_i: int, segment: Segment
    ) -> int:
        """
        Parse stage direction following a shot heading.

        Returns the index of the last line parsed.
        """
        i = start_i
        direction_lines = []

        while i < len(lines):
            line = lines[i]

            # Stop at next heading, dialogue, or transition
            if (
                self._parse_shot_heading(line, i)
                or self._parse_transition(line)
                or self.center_indent.match(line)
            ):
                break

            # Skip empty lines at the beginning
            if not direction_lines and not line.strip():
                i += 1
                continue

            # Stop at double empty lines
            if not line.strip() and i + 1 < len(lines) and not lines[i + 1].strip():
                break

            direction_lines.append(line)
            i += 1

        if direction_lines:
            content = "\n".join(direction_lines).strip()
            segment.content = content
            segment.capitalized_words = self._extract_caps(content)
            segment.end_pos = i - 1

        return i

    def _extract_caps(self, text: str) -> List[str]:
        """Extract capitalized words/phrases from stage direction."""
        caps = []

        # Find all caps words (at least 2 chars)
        for match in self.inline_caps.finditer(text):
            word = match.group()
            if len(word) > 1 and word not in ["I", "A", "OK"]:
                caps.append(word)

        return caps

    def _extract_title(self, text: str) -> str:
        """Extract screenplay title from text."""
        lines = text.split("\n")

        # Look for title in first few lines
        for line in lines[:20]:
            line = line.strip()
            if line and line.isupper() and len(line) > 5:
                # Check if it looks like a title (not a heading)
                if not any(
                    keyword in line
                    for keyword in ["INT.", "EXT.", "FADE", "CUT"]
                ):
                    return line

        return "Untitled Screenplay"

    def parse_file(self, filepath: str) -> Screenplay:
        """
        Parse a screenplay file.

        Args:
            filepath: Path to screenplay file

        Returns:
            Parsed Screenplay object
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

        screenplay = self.parse(text)
        screenplay.metadata["source_file"] = str(path.absolute())
        screenplay.metadata["file_size"] = path.stat().st_size

        if not screenplay.title or screenplay.title == "Untitled Screenplay":
            # Use filename as title
            screenplay.title = path.stem.replace("_", " ").title()

        return screenplay