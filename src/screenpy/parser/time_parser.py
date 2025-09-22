"""
Time expression parser for detecting and parsing time of day expressions.
"""

import re
from typing import Optional, List, Set
from datetime import datetime


class TimeParser:
    """
    Parses time expressions in shot headings.

    Detects various formats:
    - Standard times (DAY, NIGHT, MORNING, etc.)
    - Specific times (3 AM, 10:30 PM)
    - Dates (MARCH 15, 1999)
    - Relative times (LATER, CONTINUOUS)
    - Seasonal/holiday references
    """

    def __init__(self):
        self._init_time_words()
        self._init_patterns()

    def _init_time_words(self):
        """Initialize sets of time-related words."""
        # Time of day
        self.times_of_day = {
            "DAWN", "SUNRISE", "MORNING", "FORENOON",
            "NOON", "MIDDAY", "AFTERNOON",
            "DUSK", "SUNSET", "TWILIGHT", "EVENING",
            "NIGHT", "MIDNIGHT", "LATE NIGHT",
            "DAYBREAK", "SUNUP", "SUNDOWN",
            "FIRST LIGHT", "BREAK OF DAY",
        }

        # Relative times
        self.relative_times = {
            "LATER", "MOMENTS LATER", "SECONDS LATER",
            "MINUTES LATER", "HOURS LATER", "DAYS LATER",
            "WEEKS LATER", "MONTHS LATER", "YEARS LATER",
            "EARLIER", "BEFORE", "AFTER",
            "CONTINUOUS", "CONTINUOUS ACTION", "CONT'D",
            "SAME TIME", "SAME", "MEANWHILE",
            "SIMULTANEOUSLY", "PRESENT", "PAST", "FUTURE",
            "FLASHBACK", "FLASHFORWARD",
        }

        # Seasons
        self.seasons = {
            "SPRING", "SUMMER", "FALL", "AUTUMN", "WINTER",
        }

        # Days of week
        self.weekdays = {
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY",
            "FRIDAY", "SATURDAY", "SUNDAY",
            "WEEKDAY", "WEEKEND",
        }

        # Months
        self.months = {
            "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
            "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
        }

        # Holidays and special occasions
        self.holidays = {
            "CHRISTMAS", "CHRISTMAS EVE", "CHRISTMAS DAY",
            "NEW YEAR", "NEW YEAR'S EVE", "NEW YEAR'S DAY",
            "THANKSGIVING", "EASTER", "EASTER SUNDAY",
            "HALLOWEEN", "VALENTINE'S DAY", "VALENTINE",
            "INDEPENDENCE DAY", "FOURTH OF JULY", "4TH OF JULY",
            "MEMORIAL DAY", "LABOR DAY", "VETERANS DAY",
            "MARTIN LUTHER KING DAY", "MLK DAY",
            "PRESIDENTS DAY", "COLUMBUS DAY",
            "MOTHER'S DAY", "FATHER'S DAY",
            "ST. PATRICK'S DAY", "CINCO DE MAYO",
            "HANUKKAH", "PASSOVER", "RAMADAN", "EID",
            "DIWALI", "LUNAR NEW YEAR", "CHINESE NEW YEAR",
            "BIRTHDAY", "WEDDING", "ANNIVERSARY",
            "GRADUATION", "PROM", "HOMECOMING",
        }

        # Weather/atmospheric conditions (sometimes used as time indicators)
        self.weather_time = {
            "STORMY", "RAINY", "SNOWY", "FOGGY", "MISTY",
            "CLEAR", "CLOUDY", "OVERCAST",
        }

        # Combine all time words
        self.all_time_words = (
            self.times_of_day |
            self.relative_times |
            self.seasons |
            self.weekdays |
            self.months |
            self.holidays |
            self.weather_time
        )

    def _init_patterns(self):
        """Initialize regex patterns for time detection."""
        # Clock times: 3:30, 10:45 PM, etc.
        self.clock_pattern = re.compile(
            r"\b\d{1,2}:\d{2}\s*(?:AM|PM|A\.M\.|P\.M\.)?\b",
            re.IGNORECASE
        )

        # Hour times: 3 AM, 10 P.M., etc.
        self.hour_pattern = re.compile(
            r"\b\d{1,2}\s*(?:AM|PM|A\.M\.|P\.M\.)\b",
            re.IGNORECASE
        )

        # Years: 1999, 2020, etc.
        self.year_pattern = re.compile(r"\b(19|20)\d{2}\b")

        # Dates: March 15, December 25th, etc.
        self.date_pattern = re.compile(
            r"\b(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\.?\s+\d{1,2}(?:ST|ND|RD|TH)?\b",
            re.IGNORECASE
        )

        # Relative day: TODAY, TOMORROW, YESTERDAY
        self.relative_day_pattern = re.compile(
            r"\b(TODAY|TOMORROW|YESTERDAY)\b",
            re.IGNORECASE
        )

        # Time period: 1960s, 80s, etc.
        self.period_pattern = re.compile(
            r"\b\d{2,4}S\b",
            re.IGNORECASE
        )

        # Military time: 0800, 1430, etc.
        self.military_pattern = re.compile(r"\b\d{4}\s*(?:HOURS|HRS)?\b")

    def is_time_expression(self, text: str) -> bool:
        """
        Check if text contains a time expression.

        Args:
            text: Text to check

        Returns:
            True if text contains time expression
        """
        if not text:
            return False

        text_upper = text.upper().strip()

        # Check against time word sets
        for word in self.all_time_words:
            if word in text_upper:
                return True

        # Check regex patterns
        if (
            self.clock_pattern.search(text) or
            self.hour_pattern.search(text) or
            self.year_pattern.search(text) or
            self.date_pattern.search(text) or
            self.relative_day_pattern.search(text) or
            self.period_pattern.search(text) or
            self.military_pattern.search(text)
        ):
            return True

        # Try to parse as date
        if self._try_parse_date(text):
            return True

        return False

    def parse_time(self, text: str) -> Optional[str]:
        """
        Parse and normalize a time expression.

        Args:
            text: Time expression text

        Returns:
            Normalized time string or None
        """
        if not text:
            return None

        text = text.strip()

        # Return as-is for now (can add normalization later)
        # This is where we could standardize formats
        return text

    def _try_parse_date(self, text: str) -> bool:
        """
        Try to parse text as a date.

        Args:
            text: Text to parse

        Returns:
            True if successfully parsed as date
        """
        try:
            # Only try if it looks like it might be a date
            if len(text) > 20:  # Too long, probably not a date
                return False

            # Don't parse single words that aren't months/days
            if " " not in text and text.upper() not in self.months | self.weekdays:
                return False

            # Simple date parsing - check for common patterns
            if any(month in text.upper() for month in self.months):
                return True

            if re.search(r'\b\d{1,2}[,/]\s*\d{4}\b', text):
                return True

            return False
        except (ValueError, TypeError):
            return False

    def extract_time_components(self, text: str) -> dict:
        """
        Extract structured time components from text.

        Args:
            text: Time expression text

        Returns:
            Dictionary with extracted components
        """
        components = {
            "time_of_day": None,
            "relative_time": None,
            "date": None,
            "season": None,
            "holiday": None,
            "year": None,
            "clock_time": None,
        }

        if not text:
            return components

        text_upper = text.upper()

        # Check time of day
        for tod in self.times_of_day:
            if tod in text_upper:
                components["time_of_day"] = tod
                break

        # Check relative time
        for rel in self.relative_times:
            if rel in text_upper:
                components["relative_time"] = rel
                break

        # Check season
        for season in self.seasons:
            if season in text_upper:
                components["season"] = season
                break

        # Check holiday
        for holiday in self.holidays:
            if holiday in text_upper:
                components["holiday"] = holiday
                break

        # Extract year
        year_match = self.year_pattern.search(text)
        if year_match:
            components["year"] = year_match.group()

        # Extract clock time
        clock_match = self.clock_pattern.search(text)
        if clock_match:
            components["clock_time"] = clock_match.group()
        else:
            hour_match = self.hour_pattern.search(text)
            if hour_match:
                components["clock_time"] = hour_match.group()

        return components