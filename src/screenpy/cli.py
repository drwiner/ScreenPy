"""
Command-line interface for ScreenPy.
"""

import json
import sys
from pathlib import Path
from typing import Optional, List
import click
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich import print as rprint

from screenpy import ScreenplayParser
from screenpy.models import Screenplay


console = Console()


@click.group()
@click.version_option(version="2.0.0", prog_name="ScreenPy")
def main():
    """ScreenPy - Automated Screenplay Annotation Tool"""
    pass


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output JSON file path"
)
@click.option(
    "--pretty/--compact",
    default=True,
    help="Pretty print JSON output"
)
@click.option(
    "--stats/--no-stats",
    default=True,
    help="Show parsing statistics"
)
def parse(input_file: str, output: Optional[str], pretty: bool, stats: bool):
    """Parse a single screenplay file."""
    console.print(f"[blue]Parsing screenplay:[/blue] {input_file}")

    # Parse the screenplay
    parser = ScreenplayParser()

    try:
        screenplay = parser.parse_file(input_file)
        console.print(f"[green]✓[/green] Successfully parsed: {screenplay.title}")
    except Exception as e:
        console.print(f"[red]✗ Error parsing file:[/red] {e}")
        sys.exit(1)

    # Show statistics if requested
    if stats:
        show_statistics(screenplay)

    # Save output if specified
    if output:
        save_output(screenplay, output, pretty)
    else:
        # Print to console
        if pretty:
            rprint(json.dumps(screenplay.to_json(), indent=2))
        else:
            print(json.dumps(screenplay.to_json()))


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "-o", "--output-dir",
    type=click.Path(),
    required=True,
    help="Output directory for JSON files"
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Process subdirectories recursively"
)
@click.option(
    "--pattern",
    default="*.txt",
    help="File pattern to match (default: *.txt)"
)
def batch(input_dir: str, output_dir: str, recursive: bool, pattern: str):
    """Batch process multiple screenplay files."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Find files to process
    if recursive:
        files = list(input_path.rglob(pattern))
    else:
        files = list(input_path.glob(pattern))

    if not files:
        console.print(f"[yellow]No files found matching pattern:[/yellow] {pattern}")
        return

    console.print(f"[blue]Found {len(files)} files to process[/blue]")

    # Process files
    parser = ScreenplayParser()
    success_count = 0
    error_count = 0
    errors = []

    for file_path in track(files, description="Processing screenplays..."):
        try:
            screenplay = parser.parse_file(str(file_path))

            # Determine output path
            relative_path = file_path.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix(".json")
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Save output
            with open(output_file, "w") as f:
                json.dump(screenplay.to_json(), f, indent=2)

            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append((str(file_path), str(e)))

    # Report results
    console.print(f"\n[green]✓ Successfully processed:[/green] {success_count} files")
    if error_count:
        console.print(f"[red]✗ Errors:[/red] {error_count} files")
        if click.confirm("Show error details?"):
            for file_path, error in errors:
                console.print(f"  [red]{file_path}:[/red] {error}")


@main.command()
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output CSV file for statistics"
)
@click.option(
    "--by-genre/--all",
    default=False,
    help="Group statistics by genre"
)
def stats(input_dir: str, output: Optional[str], by_genre: bool):
    """Generate statistics from parsed screenplays."""
    input_path = Path(input_dir)

    # Find JSON files
    json_files = list(input_path.rglob("*.json"))

    if not json_files:
        console.print("[yellow]No JSON files found[/yellow]")
        return

    console.print(f"[blue]Analyzing {len(json_files)} screenplays...[/blue]")

    # Collect statistics
    stats_data = []

    for json_file in track(json_files, description="Analyzing..."):
        try:
            with open(json_file, "r") as f:
                data = json.load(f)
                screenplay = Screenplay.from_json(data)

            stats = calculate_statistics(screenplay)
            stats["file"] = json_file.stem

            # Try to detect genre from path
            if by_genre:
                parts = json_file.parts
                for part in parts:
                    if part in ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Thriller"]:
                        stats["genre"] = part
                        break

            stats_data.append(stats)
        except Exception as e:
            console.print(f"[red]Error reading {json_file}:[/red] {e}")

    # Display or save statistics
    if output:
        save_statistics_csv(stats_data, output)
        console.print(f"[green]Statistics saved to:[/green] {output}")
    else:
        display_statistics_table(stats_data, by_genre)


def show_statistics(screenplay: Screenplay):
    """Display screenplay statistics."""
    stats = calculate_statistics(screenplay)

    table = Table(title=f"Statistics for {screenplay.title}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    for key, value in stats.items():
        if key != "file":
            table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


def calculate_statistics(screenplay: Screenplay) -> dict:
    """Calculate statistics for a screenplay."""
    master_segments = [s for s in screenplay.segments if s.is_master_segment]
    dialogue_segments = [s for s in screenplay.segments if s.dialogue]

    stats = {
        "total_segments": len(screenplay.segments),
        "master_segments": len(master_segments),
        "dialogue_segments": len(dialogue_segments),
        "transitions": len(screenplay.transitions),
        "characters": len(screenplay.characters),
        "total_dialogue": sum(screenplay.characters.values()),
    }

    # Count shot types
    shot_types = {}
    for segment in screenplay.segments:
        if segment.heading and segment.heading.shot_type:
            shot_type = str(segment.heading.shot_type)
            shot_types[shot_type] = shot_types.get(shot_type, 0) + 1

    stats["shot_types"] = len(shot_types)

    # Count segments with time of day
    with_tod = sum(
        1 for s in screenplay.segments
        if s.heading and s.heading.time_of_day
    )
    stats["segments_with_tod"] = with_tod

    return stats


def save_output(screenplay: Screenplay, output_path: str, pretty: bool):
    """Save screenplay to JSON file."""
    with open(output_path, "w") as f:
        if pretty:
            json.dump(screenplay.to_json(), f, indent=2)
        else:
            json.dump(screenplay.to_json(), f)

    console.print(f"[green]✓ Output saved to:[/green] {output_path}")


def save_statistics_csv(stats_data: List[dict], output_path: str):
    """Save statistics to CSV file."""
    import csv

    if not stats_data:
        return

    # Get all keys
    keys = set()
    for stats in stats_data:
        keys.update(stats.keys())

    keys = sorted(keys)

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(stats_data)


def display_statistics_table(stats_data: List[dict], by_genre: bool):
    """Display statistics in a table."""
    if by_genre:
        # Group by genre
        genres = {}
        for stats in stats_data:
            genre = stats.get("genre", "Unknown")
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(stats)

        for genre, genre_stats in genres.items():
            table = Table(title=f"Statistics for {genre} ({len(genre_stats)} films)")
            table.add_column("Metric", style="cyan")
            table.add_column("Average", style="green")
            table.add_column("Min", style="yellow")
            table.add_column("Max", style="red")

            # Calculate aggregates
            metrics = [
                "total_segments", "master_segments", "dialogue_segments",
                "transitions", "characters", "total_dialogue"
            ]

            for metric in metrics:
                values = [s.get(metric, 0) for s in genre_stats]
                if values:
                    avg = sum(values) / len(values)
                    table.add_row(
                        metric.replace("_", " ").title(),
                        f"{avg:.1f}",
                        str(min(values)),
                        str(max(values))
                    )

            console.print(table)
            console.print()
    else:
        # Overall statistics
        table = Table(title=f"Overall Statistics ({len(stats_data)} screenplays)")
        table.add_column("Metric", style="cyan")
        table.add_column("Average", style="green")
        table.add_column("Min", style="yellow")
        table.add_column("Max", style="red")

        metrics = [
            "total_segments", "master_segments", "dialogue_segments",
            "transitions", "characters", "total_dialogue"
        ]

        for metric in metrics:
            values = [s.get(metric, 0) for s in stats_data]
            if values:
                avg = sum(values) / len(values)
                table.add_row(
                    metric.replace("_", " ").title(),
                    f"{avg:.1f}",
                    str(min(values)),
                    str(max(values))
                )

        console.print(table)


if __name__ == "__main__":
    main()