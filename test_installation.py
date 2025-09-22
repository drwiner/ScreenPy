#!/usr/bin/env python3
"""
Quick test script to verify ScreenPy installation and functionality.
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from screenpy import ScreenplayParser
        print("✅ Core parser imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import core parser: {e}")
        return False

    try:
        from screenpy.models import Screenplay, ShotHeading, Segment
        print("✅ Models imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import models: {e}")
        return False

    try:
        from screenpy.parser.grammar import SHOT_TYPES, TIME_WORDS
        print("✅ Grammar imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import grammar: {e}")
        return False

    try:
        from screenpy.vsd import VerbSenseAnalyzer
        print("✅ VSD module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import VSD: {e}")
        return False

    return True

def test_basic_parsing():
    """Test basic parsing functionality."""
    print("\nTesting basic parsing...")

    try:
        from screenpy import ScreenplayParser

        # Simple test screenplay
        test_script = """
INT. TEST ROOM - DAY

JOHN sits at a table.

JOHN
Hello, world!

CUT TO:

EXT. STREET - NIGHT

JOHN walks alone.
"""

        parser = ScreenplayParser()
        screenplay = parser.parse(test_script)

        print(f"✅ Parsed screenplay with {len(screenplay.segments)} segments")
        print(f"✅ Found {len(screenplay.characters)} characters: {list(screenplay.characters.keys())}")
        print(f"✅ Found {len(screenplay.transitions)} transitions")

        # Test shot heading parsing
        master_segments = [s for s in screenplay.segments if s.is_master_segment]
        print(f"✅ Found {len(master_segments)} master segments")

        return True

    except Exception as e:
        print(f"❌ Parsing test failed: {e}")
        return False

def test_cli_available():
    """Test that CLI is available."""
    print("\nTesting CLI availability...")

    try:
        from screenpy.cli import main
        print("✅ CLI module available")
        return True
    except ImportError as e:
        print(f"❌ CLI not available: {e}")
        return False

def test_project_structure():
    """Test that project structure is correct."""
    print("\nTesting project structure...")

    expected_paths = [
        "src/screenpy/__init__.py",
        "src/screenpy/models.py",
        "src/screenpy/cli.py",
        "src/screenpy/parser/__init__.py",
        "src/screenpy/parser/core.py",
        "src/screenpy/parser/grammar.py",
        "src/screenpy/parser/shot_parser.py",
        "src/screenpy/parser/time_parser.py",
        "src/screenpy/vsd/__init__.py",
        "src/screenpy/vsd/analyzer.py",
        "tests/test_parser.py",
        "examples/parse_screenplay.py",
        "pyproject.toml",
        "requirements.txt",
        "README.md",
    ]

    missing = []
    for path in expected_paths:
        if not Path(path).exists():
            missing.append(path)

    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All expected files present")
        return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("ScreenPy Installation Test")
    print("=" * 60)

    all_passed = True

    # Test imports
    if not test_imports():
        all_passed = False

    # Test basic parsing
    if not test_basic_parsing():
        all_passed = False

    # Test CLI
    if not test_cli_available():
        all_passed = False

    # Test structure
    if not test_project_structure():
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! ScreenPy is ready to use.")
        print("\nNext steps:")
        print("1. pip install -e .")
        print("2. Run: python examples/parse_screenplay.py")
        print("3. Try: screenpy parse <screenplay.txt>")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()