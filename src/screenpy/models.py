"""
Data models for screenplay elements using Pydantic for validation.
"""

from typing import List, Optional, Dict, Any, Tuple
from enum import Enum
from pydantic import BaseModel, Field


class LocationType(str, Enum):
    """Types of locations in shot headings."""
    INTERIOR = "INT."
    EXTERIOR = "EXT."
    INT_EXT = "INT./EXT."
    NONE = ""


class SegmentType(str, Enum):
    """Types of screenplay segments."""
    SHOT_HEADING = "shot_heading"
    STAGE_DIRECTION = "stage_direction"
    DIALOGUE = "dialogue"
    TRANSITION = "transition"
    CHARACTER = "character"


class ShotType(str, Enum):
    """Common shot types in screenplays."""
    EXTREME_WIDE = "EXTREME WIDE"
    WIDE = "WIDE"
    LONG_SHOT = "LONG SHOT"
    FULL_SHOT = "FULL SHOT"
    MEDIUM = "MEDIUM"
    CLOSE = "CLOSE"
    EXTREME_CLOSE = "EXTREME CLOSE"
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
    OTHER = "OTHER"


class TransitionType(str, Enum):
    """Types of scene transitions."""
    CUT_TO = "CUT TO"
    FADE_IN = "FADE IN"
    FADE_OUT = "FADE OUT"
    DISSOLVE_TO = "DISSOLVE TO"
    MATCH_CUT = "MATCH CUT"
    HARD_CUT = "HARD CUT"
    WIPE_TO = "WIPE TO"
    OTHER = "OTHER"


class ShotHeading(BaseModel):
    """
    Represents a parsed shot heading with structured components.

    Based on the grammar defined in the INT17 paper:
    - Location type (INT/EXT)
    - Location hierarchy (increasingly specific)
    - Shot type
    - Subject
    - Time of day
    """
    location_type: LocationType = Field(default=LocationType.NONE)
    locations: List[str] = Field(default_factory=list)
    shot_type: Optional[ShotType] = None
    shot_modifier: Optional[str] = None
    subject: Optional[str] = None
    time_of_day: Optional[str] = None
    raw_text: str
    start_pos: int
    end_pos: int
    is_master: bool = Field(
        description="True if this is a master shot heading (has location_type)"
    )

    class Config:
        json_encoders = {
            LocationType: lambda v: v.value,
            ShotType: lambda v: v.value if v else None,
        }


class Character(BaseModel):
    """Represents a character in dialogue."""
    name: str
    modifier: Optional[str] = None  # e.g., (V.O.), (O.S.)


class Dialogue(BaseModel):
    """Represents character dialogue."""
    character: Character
    parenthetical: Optional[str] = None
    text: str


class Transition(BaseModel):
    """Represents a scene transition."""
    type: TransitionType
    text: str
    from_segment: Optional[int] = None
    to_segment: Optional[int] = None


class Segment(BaseModel):
    """
    Represents a screenplay segment (scene or sub-scene).
    """
    id: int
    type: SegmentType
    heading: Optional[ShotHeading] = None
    content: str
    dialogue: Optional[Dialogue] = None
    transition: Optional[Transition] = None
    capitalized_words: List[str] = Field(default_factory=list)
    parent_segment_id: Optional[int] = None
    child_segment_ids: List[int] = Field(default_factory=list)
    start_pos: int
    end_pos: int

    @property
    def is_master_segment(self) -> bool:
        """Check if this is a master segment."""
        return self.heading and self.heading.is_master


class VerbSense(BaseModel):
    """Represents verb sense disambiguation results."""
    verb: str
    synsets: List[str] = Field(default_factory=list)
    frames: List[str] = Field(default_factory=list)
    clause_type: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class ActionInstance(BaseModel):
    """Represents an extracted action from stage direction."""
    verb: str
    agent: Optional[str] = None
    patient: Optional[str] = None
    location: Optional[str] = None
    verb_sense: Optional[VerbSense] = None
    text: str


class Screenplay(BaseModel):
    """
    Complete parsed screenplay with hierarchical structure.
    """
    title: str
    segments: List[Segment]
    transitions: List[Transition] = Field(default_factory=list)
    characters: Dict[str, int] = Field(
        default_factory=dict,
        description="Character name to occurrence count"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @property
    def master_segments(self) -> List[Segment]:
        """Get all master segments."""
        return [s for s in self.segments if s.is_master_segment]

    @property
    def dialogue_segments(self) -> List[Segment]:
        """Get all dialogue segments."""
        return [s for s in self.segments if s.type == SegmentType.DIALOGUE]

    def to_json(self) -> Dict[str, Any]:
        """Export screenplay to JSON format."""
        return self.dict()

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Screenplay":
        """Load screenplay from JSON format."""
        return cls(**data)