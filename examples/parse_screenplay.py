#!/usr/bin/env python3
"""
Example script for parsing a screenplay with ScreenPy.
"""

import json
from pathlib import Path
from screenpy import ScreenplayParser


def main():
    """Demonstrate screenplay parsing."""

    # Example screenplay text
    screenplay_text = """
THE MATRIX

FADE IN:

INT. HEART O' THE CITY HOTEL - NIGHT

The hotel was abandoned after a fire licked its way
across the polyester carpeting, destroying several
rooms as it spooled soot up the walls and ceiling.

TRINITY
(V.O.)
I know why you're here, Neo.

We MOVE CLOSER, closing in as the monitor seems to
rush at us, DIVING INTO the computer screen.

CUT TO:

INT. ROOM 303 - NIGHT

TRINITY is a beautiful woman in black leather.

TRINITY
I know what you've been doing.
I know why you hardly sleep,
why you live alone and why,
night after night, you sit
at your computer.

She walks to the window.

TRINITY (CONT'D)
You're looking for him.

ANGLE ON NEO

NEO, a man in his early thirties, watches her intently.

NEO
Who?

TRINITY
You know who I'm talking about.

NEO
Morpheus.

TRINITY
(smiling)
Yes. I know you think you're
looking for him, but he's
looking for you.

CLOSE ON NEO'S FACE

Confusion and hope battle in his expression.

EXT. CITY STREET - CONTINUOUS

The city sprawls endlessly under a starless sky.

FADE OUT.
"""

    # Create parser
    parser = ScreenplayParser()

    # Parse the screenplay
    print("Parsing screenplay...")
    screenplay = parser.parse(screenplay_text)

    print(f"\n✅ Successfully parsed: {screenplay.title}")
    print(f"Total segments: {len(screenplay.segments)}")
    print(f"Master segments: {len(screenplay.master_segments)}")
    print(f"Dialogue segments: {len(screenplay.dialogue_segments)}")
    print(f"Characters: {', '.join(screenplay.characters.keys())}")
    print(f"Transitions: {len(screenplay.transitions)}")

    # Analyze shot headings
    print("\n📍 Shot Headings:")
    for segment in screenplay.segments[:10]:  # First 10 segments
        if segment.heading:
            heading = segment.heading
            parts = []

            if heading.location_type:
                parts.append(f"Type: {heading.location_type}")
            if heading.locations:
                parts.append(f"Location: {' - '.join(heading.locations)}")
            if heading.shot_type:
                parts.append(f"Shot: {heading.shot_type}")
            if heading.subject:
                parts.append(f"Subject: {heading.subject}")
            if heading.time_of_day:
                parts.append(f"Time: {heading.time_of_day}")

            print(f"  • {heading.raw_text}")
            if parts:
                print(f"    [{', '.join(parts)}]")

    # Analyze dialogue
    print("\n💬 Dialogue Analysis:")
    for char, count in screenplay.characters.items():
        print(f"  • {char}: {count} lines")

    # Show some dialogue examples
    print("\n📝 Sample Dialogue:")
    dialogue_count = 0
    for segment in screenplay.segments:
        if segment.dialogue and dialogue_count < 3:
            d = segment.dialogue
            print(f"\n  {d.character.name}", end="")
            if d.character.modifier:
                print(f" ({d.character.modifier})", end="")
            print(":")
            if d.parenthetical:
                print(f"    {d.parenthetical}")
            # Show first 100 chars of dialogue
            text = d.text[:100] + "..." if len(d.text) > 100 else d.text
            print(f"    \"{text}\"")
            dialogue_count += 1

    # Export to JSON
    print("\n💾 Exporting to JSON...")
    output_file = "matrix_sample.json"
    with open(output_file, "w") as f:
        json.dump(screenplay.to_json(), f, indent=2)
    print(f"Saved to: {output_file}")

    # Show JSON structure sample
    print("\n📊 JSON Structure (first segment):")
    if screenplay.segments:
        first_segment = screenplay.segments[0].model_dump()
        print(json.dumps(first_segment, indent=2, default=str)[:500] + "...")


def parse_file_example():
    """Example of parsing a file."""
    parser = ScreenplayParser()

    # Example: Parse a file (if it exists)
    screenplay_file = "data/screenplays/sample.txt"

    if Path(screenplay_file).exists():
        print(f"Parsing file: {screenplay_file}")
        screenplay = parser.parse_file(screenplay_file)
        print(f"Parsed: {screenplay.title}")
        print(f"Segments: {len(screenplay.segments)}")
    else:
        print(f"File not found: {screenplay_file}")
        print("Place a screenplay .txt file at this path to test file parsing")


def batch_processing_example():
    """Example of batch processing multiple screenplays."""
    parser = ScreenplayParser()
    input_dir = Path("data/screenplays/imsdb_corpus/Action")

    if input_dir.exists():
        # Find all .txt files
        files = list(input_dir.glob("*.txt"))[:5]  # Process first 5

        print(f"Processing {len(files)} screenplays...")

        for file_path in files:
            try:
                screenplay = parser.parse_file(str(file_path))
                print(f"✅ {file_path.name}: {len(screenplay.segments)} segments")
            except Exception as e:
                print(f"❌ {file_path.name}: {e}")
    else:
        print(f"Directory not found: {input_dir}")
        print("Download screenplays to test batch processing")


if __name__ == "__main__":
    print("=" * 60)
    print("ScreenPy - Screenplay Parsing Example")
    print("=" * 60)

    # Run main example
    main()

    print("\n" + "=" * 60)
    print("Additional Examples")
    print("=" * 60)

    # Show file parsing example
    print("\n📄 File Parsing Example:")
    parse_file_example()

    # Show batch processing example
    print("\n📚 Batch Processing Example:")
    batch_processing_example()

    print("\n✨ Example complete!")