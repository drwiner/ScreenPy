# Migration Guide: ScreenPy 1.0 → 2.0

This guide helps migrate from the original ScreenPy implementation to the modernized version.

## 🏗️ Major Changes

### Project Structure
- **Old**: Flat file structure with mixed code and data
- **New**: Organized package structure under `src/screenpy/`

### Python Version
- **Old**: Python 2.7 compatible
- **New**: Python 3.8+ required

### Dependencies
- **Old**: PyParsing 2.x, old spaCy
- **New**: PyParsing 3.x, spaCy 3.x, Pydantic for models

## 📦 File Mapping

| Old Location | New Location | Notes |
|--------------|--------------|-------|
| `screenpy.py` | `src/screenpy/parser/core.py` | Refactored with type hints |
| `screenpy_vars.py` | `src/screenpy/parser/grammar.py` | Updated grammar definitions |
| `screenpile.py` | `src/screenpy/parser/segmenter.py` | Improved segmentation |
| `verb_sense/*.py` | `src/screenpy/vsd/` | Modernized VSD module |
| `moviescript_crawler.py` | `src/screenpy/utils/crawler.py` | Async crawler |
| Raw screenplays | `data/screenplays/` | Organized by genre |
| Parser outputs | `data/outputs/` | JSON format |

## 🔄 Code Migration

### 1. Import Changes

**Old:**
```python
import screenpy
from screenpy_vars import SHOT_TYPES
```

**New:**
```python
from screenpy import ScreenplayParser
from screenpy.parser.grammar import SHOT_TYPES
```

### 2. Parser Usage

**Old:**
```python
# Direct function calls
segments = parse_screenplay(text)
headings = extract_shot_headings(text)
```

**New:**
```python
# Object-oriented approach
parser = ScreenplayParser()
screenplay = parser.parse(text)
headings = screenplay.master_segments
```

### 3. Data Models

**Old:**
```python
# Tuples and dictionaries
heading = ('INT.', ['OFFICE'], None, None, 'DAY', (0, 20))
segment = {'heading': heading, 'text': '...', 'caps': [...]}
```

**New:**
```python
# Pydantic models with validation
from screenpy.models import ShotHeading, Segment

heading = ShotHeading(
    location_type=LocationType.INTERIOR,
    locations=['OFFICE'],
    time_of_day='DAY',
    raw_text='INT. OFFICE - DAY',
    start_pos=0,
    end_pos=20,
    is_master=True
)
```

### 4. VSD Module

**Old:**
```python
from verb_sense.VSD import disambiguate
frames = disambiguate(text)
```

**New:**
```python
from screenpy.vsd import VerbSenseAnalyzer

analyzer = VerbSenseAnalyzer()
actions = analyzer.extract_actions(text)
```

## 🛠️ Migration Steps

### Step 1: Install New Version

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

### Step 2: Update Imports

Replace old import statements with new package structure:

```python
# Replace these patterns
# Old → New
import screenpy → from screenpy import ScreenplayParser
import screenpy_vars → from screenpy.parser.grammar import *
import screenpile → from screenpy.parser.segmenter import *
from verb_sense import * → from screenpy.vsd import *
```

### Step 3: Convert Data

Use the migration script to convert old format files:

```bash
# Convert old JSON outputs to new format
python scripts/migrate_data.py data/old_outputs/ data/new_outputs/

# Batch convert screenplays
screenpy migrate-batch data/screenplays/ -o data/outputs/
```

### Step 4: Update Processing Scripts

**Old Script:**
```python
#!/usr/bin/env python
import screenpy
import json

text = open('screenplay.txt').read()
segments = screenpy.parse(text)
json.dump(segments, open('output.json', 'w'))
```

**New Script:**
```python
#!/usr/bin/env python3
from screenpy import ScreenplayParser
import json

parser = ScreenplayParser()
screenplay = parser.parse_file('screenplay.txt')
screenplay.to_json_file('output.json')
```

## 🔍 API Differences

### Parsing

| Operation | Old API | New API |
|-----------|---------|---------|
| Parse file | `parse_screenplay(open(f).read())` | `parser.parse_file(f)` |
| Parse text | `parse_screenplay(text)` | `parser.parse(text)` |
| Get headings | `extract_headings(text)` | `screenplay.master_segments` |
| Get dialogue | `extract_dialogue(text)` | `screenplay.dialogue_segments` |

### Data Access

| Data | Old Access | New Access |
|------|------------|------------|
| Scene location | `heading[1]` | `heading.locations` |
| Time of day | `heading[4]` | `heading.time_of_day` |
| Dialogue speaker | `segment['speaker']` | `segment.dialogue.character.name` |
| Segment text | `segment['text']` | `segment.content` |

## 🐛 Common Issues

### Issue 1: Import Errors
```python
ImportError: No module named 'screenpy'
```
**Solution**: Install the package: `pip install -e .`

### Issue 2: Python Version
```python
SyntaxError: invalid syntax (type hints)
```
**Solution**: Upgrade to Python 3.8+

### Issue 3: Missing Dependencies
```python
ModuleNotFoundError: No module named 'pydantic'
```
**Solution**: Install requirements: `pip install -r requirements.txt`

## 📚 Resources

- [New API Documentation](docs/api.md)
- [Example Scripts](examples/)
- [Test Suite](tests/)
- [GitHub Issues](https://github.com/drwiner/ScreenPy/issues)

## ❓ Questions?

For migration help, please [open an issue](https://github.com/drwiner/ScreenPy/issues) with the tag `migration`.