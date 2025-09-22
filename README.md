# ScreenPy 2.0

> **Automated Screenplay Annotation for Extracting Storytelling Knowledge**

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/paper-INT17-orange.svg)](INT17_screenplays.pdf)

ScreenPy is a Python package for parsing and analyzing screenplays to extract structured narrative elements and storytelling patterns. Based on research presented at the [Intelligent Narrative Technologies Workshop](INT17_screenplays.pdf), it provides tools for automated screenplay annotation and knowledge extraction.

## 🎬 Features

- **Screenplay Parsing**: Parse raw screenplays into structured elements
- **Shot Heading Analysis**: Extract location, shot type, subject, and time information
- **Dialogue Extraction**: Identify speakers and their dialogue with parentheticals
- **Stage Direction Processing**: Parse action descriptions and stage directions
- **Verb Sense Disambiguation**: Map actions to FrameNet frames and WordNet synsets
- **Hierarchical Structure**: Maintain scene and sub-scene relationships
- **JSON Export**: Export parsed screenplays in machine-readable format

## 📖 Paper & Research

This project implements the methodology described in:

**"Automated Screenplay Annotation for Extracting Storytelling Knowledge"**
David R. Winer and R. Michael Young
*Intelligent Narrative Technologies Workshop (INT17), 2017*

[Read the paper](INT17_screenplays.pdf)

### Key Contributions

1. **Grammar-based parsing** of shot headings following industry standards
2. **Hierarchical segmentation** of screenplay structure
3. **Verb sense disambiguation** for action extraction
4. **Large-scale corpus analysis** of 1000+ IMSDb screenplays

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/drwiner/ScreenPy.git
cd ScreenPy

# Install package
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"

# For NLP features
pip install -e ".[nlp]"
```

### Basic Usage

```python
from screenpy import ScreenplayParser

# Initialize parser
parser = ScreenplayParser()

# Parse a screenplay file
screenplay = parser.parse_file("path/to/screenplay.txt")

# Access structured elements
for segment in screenplay.master_segments:
    print(f"Scene: {segment.heading.raw_text}")
    if segment.heading.location_type:
        print(f"  Location: {' - '.join(segment.heading.locations)}")
    if segment.heading.time_of_day:
        print(f"  Time: {segment.heading.time_of_day}")

# Export to JSON
screenplay_json = screenplay.to_json()
```

### Command Line Interface

```bash
# Parse a single screenplay
screenpy parse screenplay.txt -o output.json

# Batch process screenplays
screenpy batch data/screenplays/ -o data/outputs/

# Extract verb senses with VSD
screenpy vsd screenplay.txt --frames --synsets

# Generate statistics
screenpy stats data/outputs/ -o stats.csv
```

## 📁 Project Structure

```
ScreenPy/
├── src/screenpy/           # Main package code
│   ├── parser/            # Parsing modules
│   │   ├── grammar.py     # Shot heading grammar
│   │   ├── segmenter.py   # Screenplay segmentation
│   │   └── elements.py    # Element extraction
│   ├── vsd/              # Verb Sense Disambiguation
│   │   ├── frames.py     # FrameNet integration
│   │   ├── synsets.py    # WordNet integration
│   │   └── clausie.py    # Clause extraction
│   ├── models.py         # Data models (Pydantic)
│   ├── utils.py          # Utilities
│   └── cli.py            # Command-line interface
├── tests/                # Test suite
├── data/                 # Data files
│   ├── screenplays/      # Raw screenplay files
│   └── outputs/          # Parsed outputs
├── docs/                 # Documentation
└── examples/             # Example scripts
```

## 📊 Screenplay Elements

### Shot Headings

Shot headings follow a standardized grammar:

```
INT. LOCATION - SHOT_TYPE - SUBJECT - TIME_OF_DAY
```

Examples:
- `INT. CENTRAL PARK - DAY`
- `EXT. WHITE HOUSE - SOUTH LAWN - CLOSE ON CNN CORRESPONDENT - SUNSET`
- `WIDE SHOT - RACETRACK AND EMPTY STANDS`

### Supported Elements

| Element | Description | Example |
|---------|-------------|---------|
| **Master Headings** | Scene beginnings with INT/EXT | `INT. OFFICE - DAY` |
| **Shot Types** | Camera shot specifications | `CLOSE`, `WIDE`, `TRACKING` |
| **Stage Direction** | Action descriptions | `John enters the room.` |
| **Dialogue** | Character speech | `JOHN: Hello there!` |
| **Transitions** | Scene changes | `CUT TO:`, `FADE OUT` |
| **In-line Caps** | Emphasized elements | Sound effects, character intros |

## 🔬 Verb Sense Disambiguation (VSD)

The VSD module maps verbs in stage directions to semantic frames:

```python
from screenpy.vsd import VerbSenseAnalyzer

analyzer = VerbSenseAnalyzer()

# Analyze stage direction
text = "Indy sails through sideways and rolls to a stop"
actions = analyzer.extract_actions(text)

for action in actions:
    print(f"Verb: {action.verb}")
    print(f"Frames: {action.verb_sense.frames}")
    print(f"Synsets: {action.verb_sense.synsets}")
```

## 📈 Corpus Statistics

Analysis of 1000+ IMSDb screenplays:

| Genre | Films | Avg Segments | Avg Headings | Avg Dialogue |
|-------|-------|--------------|--------------|--------------|
| Action | 272 | 1240 | 621 | 538 |
| Comedy | 310 | 1370 | 582 | 720 |
| Drama | 541 | 1328 | 591 | 667 |
| Horror | 134 | 1150 | 632 | 451 |
| Sci-Fi | 140 | 1161 | 607 | 472 |

[Full statistics](docs/statistics.md)

## 🛠️ Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black src/ tests/

# Type checking
mypy src/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Documentation

- [API Reference](docs/api.md)
- [Parsing Grammar](docs/grammar.md)
- [VSD Methodology](docs/vsd.md)
- [Examples](examples/)

## 🔗 Related Work

- [IMSDb](https://www.imsdb.com) - Internet Movie Script Database
- [FrameNet](https://framenet.icsi.berkeley.edu) - Frame semantic annotations
- [WordNet](https://wordnet.princeton.edu) - Lexical database
- [spaCy](https://spacy.io) - Industrial-strength NLP
- [sense2vec](https://github.com/explosion/sense2vec) - Semantic similarity

## 📄 Citation

If you use ScreenPy in your research, please cite:

```bibtex
@inproceedings{winer2017screenpy,
  title={Automated Screenplay Annotation for Extracting Storytelling Knowledge},
  author={Winer, David R. and Young, R. Michael},
  booktitle={Intelligent Narrative Technologies Workshop (INT17)},
  year={2017},
  organization={AAAI}
}
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **David R. Winer** - [drwiner](https://github.com/drwiner)
- **R. Michael Young** - *Advisor*

## 🙏 Acknowledgments

- University of Utah School of Computing
- Entertainment Arts and Engineering Program
- National Science Foundation Grant No. 1654651

---

*For questions or support, please [open an issue](https://github.com/drwiner/ScreenPy/issues)*
