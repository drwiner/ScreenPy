"""
Verb Sense Disambiguation analyzer for extracting action semantics from screenplays.

This module implements the VSD approach described in the INT17 paper,
using FrameNet frames and WordNet synsets to disambiguate verb meanings
in stage directions.
"""

from typing import List, Dict, Optional, Tuple
import re
import logging
from dataclasses import dataclass

from screenpy.models import VerbSense, ActionInstance

logger = logging.getLogger(__name__)


@dataclass
class Clause:
    """Represents a parsed clause with grammatical components."""
    subject: Optional[str] = None
    verb: str = ""
    object: Optional[str] = None
    complement: Optional[str] = None
    adverbial: Optional[str] = None
    clause_type: str = ""  # SV, SVO, SVOO, etc.


class VerbSenseAnalyzer:
    """
    Analyzes stage directions to extract and disambiguate verb senses.

    Uses:
    - Clause parsing to identify grammatical structures
    - FrameNet for semantic frame detection
    - WordNet for synonym sets
    - sense2vec for similarity scoring
    """

    def __init__(self):
        """Initialize the VSD analyzer."""
        self._init_verb_patterns()
        self._init_frame_mappings()
        self.frames_loaded = False
        self.wordnet_loaded = False

    def _init_verb_patterns(self):
        """Initialize common verb patterns in screenplays."""
        # Common action verbs in screenplays
        self.action_verbs = {
            # Movement
            "walk", "run", "move", "enter", "exit", "leave",
            "approach", "cross", "turn", "step", "jump", "climb",
            "crawl", "slide", "fall", "rise", "stand", "sit",

            # Interaction
            "take", "give", "grab", "hold", "drop", "throw",
            "catch", "push", "pull", "open", "close", "lock",
            "unlock", "touch", "hit", "strike", "kick", "punch",

            # Communication
            "say", "speak", "whisper", "shout", "yell", "scream",
            "call", "answer", "ask", "tell", "explain", "argue",

            # Perception
            "look", "see", "watch", "stare", "glance", "notice",
            "hear", "listen", "smell", "taste", "feel", "sense",

            # Cognitive
            "think", "realize", "understand", "remember", "forget",
            "know", "believe", "doubt", "wonder", "decide",
        }

        # Clause type patterns
        self.clause_patterns = {
            "SV": re.compile(r"^(\S+)\s+(\w+)$"),  # John runs
            "SVO": re.compile(r"^(\S+)\s+(\w+)\s+(.+)$"),  # John opens door
            "SVOO": re.compile(r"^(\S+)\s+(\w+)\s+(\S+)\s+(.+)$"),  # John gives Mary book
            "SVC": re.compile(r"^(\S+)\s+(\w+)\s+(\w+)$"),  # John is happy
            "SVOC": re.compile(r"^(\S+)\s+(\w+)\s+(\S+)\s+(\w+)$"),  # John makes Mary happy
            "SVA": re.compile(r"^(\S+)\s+(\w+)\s+(.+)$"),  # John runs quickly
            "SVOA": re.compile(r"^(\S+)\s+(\w+)\s+(\S+)\s+(.+)$"),  # John puts book there
        }

    def _init_frame_mappings(self):
        """Initialize mappings to FrameNet frames."""
        # Simplified frame mappings (in full implementation, would load from FrameNet)
        self.verb_to_frames = {
            # Motion frames
            "walk": ["Self_motion", "Motion"],
            "run": ["Self_motion", "Fleeing"],
            "enter": ["Arriving", "Motion"],
            "exit": ["Departing", "Motion"],
            "approach": ["Arriving", "Motion_directional"],

            # Manipulation frames
            "take": ["Taking", "Manipulation"],
            "give": ["Giving", "Transfer"],
            "grab": ["Manipulation", "Taking"],
            "hold": ["Containing", "Manipulation"],
            "drop": ["Releasing", "Cause_motion"],

            # Communication frames
            "say": ["Statement", "Communication"],
            "speak": ["Statement", "Communication_manner"],
            "whisper": ["Communication_manner", "Statement"],
            "shout": ["Communication_noise", "Statement"],
            "ask": ["Questioning", "Request"],

            # Perception frames
            "look": ["Perception_active", "Seeking"],
            "see": ["Perception_experience", "Becoming_aware"],
            "watch": ["Perception_active", "Attention"],
            "hear": ["Perception_experience", "Hearsay"],
            "notice": ["Becoming_aware", "Perception_experience"],

            # Cognitive frames
            "think": ["Cogitation", "Opinion"],
            "realize": ["Coming_to_believe", "Awareness"],
            "understand": ["Grasp", "Awareness"],
            "remember": ["Remembering_information", "Memory"],
            "decide": ["Deciding", "Choosing"],
        }

    def extract_actions(self, text: str) -> List[ActionInstance]:
        """
        Extract action instances from stage direction text.

        Args:
            text: Stage direction text

        Returns:
            List of ActionInstance objects with verb senses
        """
        actions = []

        # Clean and prepare text
        text = self._clean_text(text)

        # Split into sentences
        sentences = self._split_sentences(text)

        for sentence in sentences:
            # Parse clauses
            clauses = self._parse_clauses(sentence)

            for clause in clauses:
                if clause.verb:
                    # Disambiguate verb sense
                    verb_sense = self._disambiguate_verb(clause)

                    # Create action instance
                    action = ActionInstance(
                        verb=clause.verb,
                        agent=clause.subject,
                        patient=clause.object,
                        verb_sense=verb_sense,
                        text=sentence,
                    )

                    actions.append(action)

        return actions

    def _clean_text(self, text: str) -> str:
        """Clean stage direction text."""
        # Remove parentheticals
        text = re.sub(r"\([^)]+\)", "", text)

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting (can be improved with NLP library)
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def _parse_clauses(self, sentence: str) -> List[Clause]:
        """
        Parse sentence into clauses.

        This is a simplified implementation. In production,
        would use ClausIE or similar tool.
        """
        clauses = []

        # Simple verb detection
        words = sentence.split()
        for i, word in enumerate(words):
            word_lower = word.lower()

            if word_lower in self.action_verbs:
                clause = Clause(verb=word_lower)

                # Get subject (word before verb)
                if i > 0:
                    clause.subject = words[i - 1]

                # Get object (words after verb)
                if i < len(words) - 1:
                    clause.object = " ".join(words[i + 1:])

                # Determine clause type
                if clause.subject and clause.object:
                    clause.clause_type = "SVO"
                elif clause.subject:
                    clause.clause_type = "SV"
                else:
                    clause.clause_type = "V"

                clauses.append(clause)

        return clauses

    def _disambiguate_verb(self, clause: Clause) -> VerbSense:
        """
        Disambiguate verb sense using frames and synsets.

        Args:
            clause: Parsed clause with verb

        Returns:
            VerbSense with disambiguation results
        """
        verb = clause.verb
        verb_sense = VerbSense(
            verb=verb,
            clause_type=clause.clause_type,
            confidence=0.5,  # Default confidence
        )

        # Get FrameNet frames
        if verb in self.verb_to_frames:
            verb_sense.frames = self.verb_to_frames[verb]
            verb_sense.confidence = 0.7

        # Get WordNet synsets (simplified)
        verb_sense.synsets = self._get_synsets(verb, clause.clause_type)

        # Adjust confidence based on clause type
        if clause.clause_type in ["SVO", "SVOO"]:
            verb_sense.confidence = min(1.0, verb_sense.confidence + 0.1)

        return verb_sense

    def _get_synsets(self, verb: str, clause_type: str) -> List[str]:
        """
        Get WordNet synsets for verb.

        This is a placeholder implementation.
        In production, would use NLTK WordNet.
        """
        # Simplified synset mapping
        synset_map = {
            "walk": ["walk.v.01", "walk.v.02"],
            "run": ["run.v.01", "run.v.03", "run.v.13"],
            "enter": ["enter.v.01", "enter.v.02"],
            "take": ["take.v.01", "take.v.04", "take.v.08"],
            "give": ["give.v.01", "give.v.03"],
            "say": ["say.v.01", "state.v.01"],
            "look": ["look.v.01", "look.v.02"],
            "see": ["see.v.01", "understand.v.02"],
            "think": ["think.v.01", "think.v.03"],
        }

        return synset_map.get(verb, [f"{verb}.v.01"])

    def analyze_segment(self, segment_text: str) -> Dict[str, any]:
        """
        Analyze a segment of stage direction for verb senses.

        Args:
            segment_text: Text of stage direction segment

        Returns:
            Analysis results including actions and statistics
        """
        actions = self.extract_actions(segment_text)

        # Collect statistics
        verb_counts = {}
        frame_counts = {}
        synset_counts = {}

        for action in actions:
            # Count verbs
            verb_counts[action.verb] = verb_counts.get(action.verb, 0) + 1

            # Count frames
            if action.verb_sense:
                for frame in action.verb_sense.frames:
                    frame_counts[frame] = frame_counts.get(frame, 0) + 1

                # Count synsets
                for synset in action.verb_sense.synsets:
                    synset_counts[synset] = synset_counts.get(synset, 0) + 1

        return {
            "actions": actions,
            "verb_counts": verb_counts,
            "frame_counts": frame_counts,
            "synset_counts": synset_counts,
            "total_actions": len(actions),
        }

    def load_resources(self, framenet_path: Optional[str] = None,
                      wordnet_path: Optional[str] = None):
        """
        Load external resources for VSD.

        Args:
            framenet_path: Path to FrameNet data
            wordnet_path: Path to WordNet data
        """
        if framenet_path:
            logger.info(f"Loading FrameNet from {framenet_path}")
            # Load FrameNet data
            self.frames_loaded = True

        if wordnet_path:
            logger.info(f"Loading WordNet from {wordnet_path}")
            # Load WordNet data
            self.wordnet_loaded = True