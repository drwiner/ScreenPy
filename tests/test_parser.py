"""
Tests for the screenplay parser.
"""

import pytest
from screenpy import ScreenplayParser
from screenpy.models import LocationType, SegmentType, ShotType
from screenpy.parser.shot_parser import ShotHeadingParser
from screenpy.parser.time_parser import TimeParser


class TestShotHeadingParser:
    """Test shot heading parsing."""

    def setup_method(self):
        self.parser = ShotHeadingParser()

    def test_master_heading_basic(self):
        """Test basic master heading parsing."""
        text = "INT. CENTRAL PARK - DAY"
        result = self.parser.parse(text)

        assert result is not None
        assert result.location_type == LocationType.INTERIOR
        assert result.locations == ["CENTRAL PARK"]
        assert result.time_of_day == "DAY"
        assert result.is_master

    def test_master_heading_complex(self):
        """Test complex master heading with multiple locations."""
        text = "EXT. WHITE HOUSE - SOUTH LAWN - SUNSET"
        result = self.parser.parse(text)

        assert result is not None
        assert result.location_type == LocationType.EXTERIOR
        assert result.locations == ["WHITE HOUSE", "SOUTH LAWN"]
        assert result.time_of_day == "SUNSET"

    def test_shot_heading_with_shot_type(self):
        """Test heading with shot type."""
        text = "INT. OFFICE - CLOSE ON JOHN - DAY"
        result = self.parser.parse(text)

        assert result is not None
        assert result.location_type == LocationType.INTERIOR
        assert result.locations == ["OFFICE"]
        assert result.shot_type == ShotType.CLOSE
        assert result.subject == "JOHN"
        assert result.time_of_day == "DAY"

    def test_shot_only_heading(self):
        """Test shot-only heading (non-master)."""
        text = "WIDE SHOT - RACETRACK"
        result = self.parser.parse(text)

        assert result is not None
        assert result.location_type == LocationType.NONE
        assert result.shot_type == ShotType.WIDE
        assert result.subject == "RACETRACK"
        assert not result.is_master

    def test_pov_shot(self):
        """Test POV shot parsing."""
        text = "JOHN'S POV"
        result = self.parser.parse(text)

        assert result is not None
        assert result.shot_type == ShotType.POV
        assert not result.is_master

    def test_tracking_shot(self):
        """Test tracking shot parsing."""
        text = "TRACKING SHOT - THROUGH THE FOREST"
        result = self.parser.parse(text)

        assert result is not None
        assert result.shot_type == ShotType.TRACKING
        assert result.subject == "THROUGH THE FOREST"

    def test_time_only_heading(self):
        """Test heading with only time."""
        text = "MIDNIGHT"
        result = self.parser.parse(text)

        assert result is not None
        assert result.time_of_day == "MIDNIGHT"

    def test_int_ext_heading(self):
        """Test INT./EXT. heading."""
        text = "INT./EXT. CAR - MOVING - DAY"
        result = self.parser.parse(text)

        assert result is not None
        assert result.location_type == LocationType.INT_EXT
        assert result.locations == ["CAR", "MOVING"]
        assert result.time_of_day == "DAY"


class TestTimeParser:
    """Test time expression parsing."""

    def setup_method(self):
        self.parser = TimeParser()

    def test_standard_times(self):
        """Test standard time of day expressions."""
        times = ["DAY", "NIGHT", "MORNING", "AFTERNOON", "DUSK", "DAWN"]

        for time in times:
            assert self.parser.is_time_expression(time)

    def test_clock_times(self):
        """Test clock time expressions."""
        times = ["3 AM", "10:30 PM", "12:00", "6 P.M."]

        for time in times:
            assert self.parser.is_time_expression(time)

    def test_relative_times(self):
        """Test relative time expressions."""
        times = ["LATER", "MOMENTS LATER", "CONTINUOUS", "SAME TIME"]

        for time in times:
            assert self.parser.is_time_expression(time)

    def test_holidays(self):
        """Test holiday detection."""
        holidays = ["CHRISTMAS EVE", "NEW YEAR'S DAY", "THANKSGIVING"]

        for holiday in holidays:
            assert self.parser.is_time_expression(holiday)

    def test_dates(self):
        """Test date detection."""
        dates = ["MARCH 15", "DECEMBER 25TH", "JULY 4, 1776"]

        for date in dates:
            assert self.parser.is_time_expression(date)

    def test_not_time(self):
        """Test non-time expressions."""
        not_times = ["OFFICE", "JOHN", "TABLE", "DOOR"]

        for text in not_times:
            assert not self.parser.is_time_expression(text)

    def test_extract_components(self):
        """Test component extraction."""
        text = "CHRISTMAS EVE, 1999 - MIDNIGHT"
        components = self.parser.extract_time_components(text)

        assert components["holiday"] == "CHRISTMAS EVE"
        assert components["year"] == "1999"
        assert components["time_of_day"] == "MIDNIGHT"


class TestScreenplayParser:
    """Test full screenplay parsing."""

    def setup_method(self):
        self.parser = ScreenplayParser()

    def test_parse_simple_screenplay(self):
        """Test parsing a simple screenplay."""
        text = """
FADE IN:

INT. OFFICE - DAY

John sits at his desk.

JOHN
Hello, world!

MARY
(surprised)
What did you say?

CUT TO:

EXT. STREET - NIGHT

They walk together.

FADE OUT.
"""
        screenplay = self.parser.parse(text)

        assert screenplay is not None
        assert len(screenplay.segments) > 0
        assert len(screenplay.characters) == 2
        assert "JOHN" in screenplay.characters
        assert "MARY" in screenplay.characters

    def test_parse_master_and_sub_segments(self):
        """Test hierarchical segment parsing."""
        text = """
INT. HOUSE - DAY

LIVING ROOM

John enters.

KITCHEN

Mary cooks.

EXT. GARDEN - CONTINUOUS

Birds chirp.
"""
        screenplay = self.parser.parse(text)

        # Find master segments
        master_segments = [s for s in screenplay.segments if s.is_master_segment]
        assert len(master_segments) == 2  # INT. HOUSE and EXT. GARDEN

    def test_parse_transitions(self):
        """Test transition parsing."""
        text = """
INT. OFFICE - DAY

John works.

CUT TO:

EXT. STREET - NIGHT

John walks.

MATCH CUT TO:

INT. HOME - NIGHT

John sleeps.
"""
        screenplay = self.parser.parse(text)

        assert len(screenplay.transitions) == 2

    def test_parse_dialogue_with_parenthetical(self):
        """Test dialogue with parenthetical parsing."""
        text = """
INT. ROOM - DAY

JOHN
(angrily)
I can't believe this!

MARY
(O.S.)
Neither can I.
"""
        screenplay = self.parser.parse(text)

        dialogue_segments = [s for s in screenplay.segments if s.dialogue]
        assert len(dialogue_segments) == 2

        # Check first dialogue
        john_dialogue = dialogue_segments[0].dialogue
        assert john_dialogue.character.name == "JOHN"
        assert john_dialogue.parenthetical == "(angrily)"
        assert "can't believe" in john_dialogue.text

        # Check second dialogue with modifier
        mary_dialogue = dialogue_segments[1].dialogue
        assert mary_dialogue.character.name == "MARY"
        assert mary_dialogue.character.modifier == "O.S."

    def test_extract_caps_from_stage_direction(self):
        """Test extraction of capitalized words from stage direction."""
        text = """
INT. SUBMARINE - NIGHT

The crew SCRAMBLES to their stations. A loud BANG echoes through the hull.
CAPTAIN SMITH enters.
"""
        screenplay = self.parser.parse(text)

        # Find stage direction segment
        stage_segments = [
            s for s in screenplay.segments
            if s.type == SegmentType.STAGE_DIRECTION and s.content
        ]

        if stage_segments:
            caps = stage_segments[0].capitalized_words
            assert "SCRAMBLES" in caps
            assert "BANG" in caps
            assert "CAPTAIN" in caps
            assert "SMITH" in caps


# Test fixtures for sample screenplays
@pytest.fixture
def sample_screenplay_text():
    """Sample screenplay text for testing."""
    return """
FADE IN:

INT. UNIVERSITY LIBRARY - DAY

DAVID, 30s, scholarly type with glasses, browses ancient texts.

ANGLE ON - MYSTERIOUS BOOK

The book glows faintly.

DAVID
(whispers)
This can't be real...

He opens the book carefully.

INSERT - BOOK PAGES

Strange symbols dance across the pages.

BACK TO DAVID

His eyes widen in amazement.

SARAH (O.S.)
David? Are you there?

DAVID
(startled)
Sarah! You have to see this!

SARAH, late 20s, adventurous spirit, enters frame.

SARAH
What is it?

CLOSE ON SARAH'S FACE

Wonder and fear mix in her expression.

CUT TO:

EXT. UNIVERSITY - MAGIC HOUR

They exit the building together, book in hand.

FADE OUT.
"""


def test_full_screenplay_parse(sample_screenplay_text):
    """Test parsing a complete screenplay sample."""
    parser = ScreenplayParser()
    screenplay = parser.parse(sample_screenplay_text)

    # Check basic structure
    assert screenplay is not None
    assert len(screenplay.segments) > 0

    # Check characters
    assert "DAVID" in screenplay.characters
    assert "SARAH" in screenplay.characters

    # Check for different segment types
    has_master = any(s.is_master_segment for s in screenplay.segments)
    has_dialogue = any(s.dialogue for s in screenplay.segments)
    has_stage_direction = any(
        s.type == SegmentType.STAGE_DIRECTION for s in screenplay.segments
    )

    assert has_master
    assert has_dialogue
    assert has_stage_direction

    # Check transitions
    assert len(screenplay.transitions) > 0